# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from .Debug import logger
from .CutListUtils import secondsToPts, ptsToSeconds
from .RecordingUtils import isStreamRecording
from .CockpitSmartSeek import CockpitSmartSeek
from .CockpitEvent import CockpitEvent
from .JobUtils import getPendingJob


class CockpitSeek(CockpitSmartSeek, CockpitEvent):

    def __init__(self, session, service, event_start, recording_start_time, timeshift, service_center):
        self.service = service
        self.path = self.service.getPath()
        self.timeshift = timeshift
        CockpitSmartSeek.__init__(self, event_start, True)
        CockpitEvent.__init__(self, session, service, recording_start_time, service_center)
        self.recording_job = getPendingJob("TMP", self.path)
        logger.info("recording_job: %s", self.recording_job)

    def isRecording(self):
        is_recording = isStreamRecording(self.path)
        return is_recording

    def getLength(self):
        length = 0
        if self.service_started:
            _, _, length, _, _ = self.getEventInfo()
            length = secondsToPts(length)
        logger.info("length: %ss (%s)", ptsToSeconds(length), length)
        return length

    def getSeekLength(self):
        length = 0
        seek = self.getSeek()
        if seek and self.service_started:
            seek_len = seek.getLength()
            if not seek_len[0]:
                length = seek_len[1]
        logger.info("length: %ss (%s)", ptsToSeconds(length), length)
        return length

    def getPosition(self):
        position = 0
        if self.service_started:
            position = self.getSeekPosition()
        logger.debug("position: %ss (%s)", ptsToSeconds(position), position)
        return position

    def getRecordingLength(self):
        _, _, length, _, _ = self.getEventInfo()
        logger.debug("recording_length: %ss (%s)", ptsToSeconds(length), length)
        return length

    def getRecordingPosition(self):
        position = 0
        if self.service_started:
            if self.isRecording():
                _, _, length, _, _ = self.getEventInfo()
                position = secondsToPts(length * self.recording_job.getProgress() / 100)
        logger.debug("recording_position: %ss (%s)", ptsToSeconds(position), position)
        return position

    def getSeekPosition(self):
        position = 0
        seek = self.getSeek()
        if seek and self.service_started:
            pos = seek.getPlayPosition()
            if not pos[0] and pos[1] > 0:
                position = pos[1]
        logger.info("position: %ss (%s)", ptsToSeconds(position), position)
        return position

    def getBeforePosition(self):
        position = 0
        return position
