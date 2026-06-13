# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import os
import re
import threading
from urllib.parse import urljoin
from twisted.internet import reactor
from Components.Task import Task
from .WebRequestsAsync import WebRequestsAsync
from .WebRequests import WebRequests
from .Debug import logger
from .ParserMetaFile import ParserMetaFile
from .FileUtils import writeFile, deleteFiles, touchFile
from .FileManagerUtils import FILE_OP_DELETE
try:
    from Plugins.SystemPlugins.CacheCockpit.FileManager import FileManager
except Exception:
    logger.error("CacheCockpit import error")
    FileManager = None


def loadDatabaseFile(target_path, event_name, short_description, description, rec_time, service_ref, length):
    logger.info("target_path: %s, event_name: %s, short_description: %s, service_ref: %s, length: %s",
                target_path, event_name, short_description, service_ref, length)
    file_name = os.path.splitext(target_path)[0]
    writeFile(file_name + ".txt", description)
    ParserMetaFile(target_path).updateMeta(
        {
            "service_reference": service_ref,
            "name": event_name,
            "description": short_description,
            "rec_time": rec_time,
            "length": length
        }
    )
    if FileManager:
        FileManager.getInstance("MVC").loadDatabaseFile(target_path)


def deleteFile(target_path):
    logger.info("target_path: %s", target_path)
    if FileManager:
        FileManager.getInstance("MVC").execFileOp(
            FILE_OP_DELETE,
            target_path,
            None,
            None
        )
    else:
        deleteFiles(os.path.splitext(target_path)[0] + ".*")


def downloadCover(url, path):
    if url:
        web_request = WebRequests()
        content = web_request.getContent(url)
        data = content if isinstance(content, str) else content.decode("utf-8", errors="replace")
        url = re.findall(r'src":"([^"]+)', data, re.DOTALL)
        if not url:
            url = re.findall(r'image" content="([^"]+)', data, re.DOTALL)
        if url:
            url = url[0]
            url = url.replace("{width}", "1080")
            if "kika.de" in url or "arte.tv" in url:
                url = url.split("?")[0]
                if "arte.tv" in url:
                    url = url + ".jpg"
            web_request.downloadFile(url, path)


class DownloadTaskFile(Task):

    TASK_NAME = "download task"

    def __init__(self, job, url, target_path, event_name, short_description, description, rec_time, service_ref, length, web_site_url):
        logger.info("job: %s, url: %s, target_path: %s, description: %s",
                    job, url, target_path, description)
        self.url = url
        self.target_path = target_path
        self.event_name = event_name
        self.short_description = short_description
        self.description = description
        self.rec_time = rec_time
        self.service_ref = service_ref
        self.web_site_url = web_site_url
        self.length = length
        self.download = WebRequestsAsync()
        self.totalbytes = 0
        self.recvbytes = 0
        self._aborted = False
        Task.__init__(self, job, self.TASK_NAME)

    def abort(self, *_args):
        logger.info("...")
        self._aborted = True
        if self.web_client:
            self.web_client.cancel()
        Task.processFinished(self, 1)

    def run(self, callback):
        logger.info("...")
        self.callback = callback
        touchFile(self.target_path)

        # Prepare cover and metadata in background to avoid blocking the main thread
        threading.Thread(target=self._prepareCoverAndMeta, daemon=True).start()

        self.web_client = self.download.downloadFileAsync(
            url=self.url,
            path=self.target_path
        )

        # Add progress, completion and error callbacks
        self.web_client.addProgback(self.http_progress)
        self.web_client.addCallback(self.http_finished)
        self.web_client.addErrback(self.http_failed)

        # Start the download
        self.web_client.start()

    def _prepareCoverAndMeta(self):
        try:
            downloadCover(self.web_site_url, os.path.splitext(self.target_path)[0] + ".jpg")
            reactor.callFromThread(
                loadDatabaseFile, self.target_path, self.event_name, self.short_description,
                self.description, self.rec_time, self.service_ref, self.length)
        except Exception as e:
            logger.error("Error preparing cover/meta: %s", e)

    def http_progress(self, recvbytes, totalbytes, progress):
        # logger.info("...")
        self.progress = int(self.end * progress / 100)
        self.recvbytes, self.totalbytes = recvbytes, totalbytes

    def http_finished(self, _result):
        # logger.info("result: %s", _result)
        reactor.callFromThread(self._on_finished)

    def _on_finished(self):
        if self._aborted:
            return
        loadDatabaseFile(self.target_path, self.event_name, self.short_description,
                         self.description, self.rec_time, self.service_ref, self.length)
        Task.processFinished(self, 0)

    def http_failed(self, error_message=""):
        logger.info("...")
        reactor.callFromThread(self._on_failed, error_message)

    def _on_failed(self, error_message=""):
        if self._aborted:
            return
        logger.error("error_message: %s", error_message)
        deleteFile(self.target_path)
        Task.processFinished(self, 1)


class DownloadTaskHLS(Task):
    totalbytes = recvbytes = 0

    def __init__(self, job, url, segments, target_path, event_name, short_description, description, rec_time, service_ref, length, web_site_url):
        logger.info("job: %s, url: %s, target_path: %s, description: %s",
                    job, url, target_path, description)
        self.url = url
        self.segments = segments
        self.target_path = target_path
        self.event_name = event_name
        self.short_description = short_description
        self.description = description
        self.web_site_url = web_site_url
        self.rec_time = rec_time
        self.service_ref = service_ref
        self.length = length
        self.content = WebRequestsAsync()
        Task.__init__(self, job, "download task")
        self.totalbytes = len(segments)
        self.file_handle = None
        self._aborted = False

    def abort(self, *_args):
        logger.info("...")
        self._aborted = True
        self.segments = []
        if self.web_client:
            self.web_client.cancel()
        if self.file_handle and not self.file_handle.closed:
            self.file_handle.close()
        Task.processFinished(self, 1)

    def run(self, callback):
        logger.info("...")
        self.callback = callback
        touchFile(self.target_path)

        # Prepare cover and metadata in background to avoid blocking the main thread
        threading.Thread(target=self._prepareCoverAndMeta, daemon=True).start()

        self.file_handle = open(self.target_path, "wb")  # pylint: disable=consider-using-with
        self.downloadSegment(
            str(urljoin(self.url, self.segments.pop(0).url)))

    def _prepareCoverAndMeta(self):
        try:
            downloadCover(self.web_site_url, os.path.splitext(self.target_path)[0] + ".jpg")
            reactor.callFromThread(
                loadDatabaseFile, self.target_path, self.event_name, self.short_description,
                self.description, self.rec_time, self.service_ref, self.length)
        except Exception as e:
            logger.error("Error preparing cover/meta: %s", e)

    def downloadSegment(self, url):
        logger.info("url: %s", url)
        self.web_client = self.content.getContentAsync(url)
        self.web_client.addCallback(
            self._http_finished_thread).addErrback(self._http_failed_thread)
        self.web_client.start()

    def _http_finished_thread(self, result):
        reactor.callFromThread(self.http_finished, result)

    def http_finished(self, result):
        if self._aborted:
            return
        # logger.info("...")
        # logger.debug("segments: %s", self.segments)
        if result:
            content = result[1] if isinstance(result, tuple) else result
            self.file_handle.write(content)
        else:
            self.segments = []
        self.recvbytes += 1
        self.progress = int(
            round(self.end * self.recvbytes / float(self.totalbytes)))
        if self.segments:
            segment = self.segments.pop(0)
            logger.debug("segment: %s", segment)
            self.downloadSegment(str(urljoin(self.url, segment.url)))
        else:
            self.file_handle.close()
            loadDatabaseFile(self.target_path, self.event_name, self.short_description,
                             self.description, self.rec_time, self.service_ref, self.length)
            Task.processFinished(self, 0)

    def _http_failed_thread(self, error):
        reactor.callFromThread(self.http_failed, error)

    def http_failed(self, error):
        if self._aborted:
            return
        logger.info("...")
        if self.file_handle and not self.file_handle.closed:
            self.file_handle.close()

        # Handle both string errors and exception objects
        error_message = str(error) if error else ""
        logger.error("error_message: %s", error_message)
        deleteFile(self.target_path)
        Task.processFinished(self, 1)
