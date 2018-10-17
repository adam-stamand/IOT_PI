import pychromecast

CAST_NAME = "Adam's Living Room"


class RpiCast():
    def __init__(self):
        chromecasts = pychromecast.get_chromecasts()
        # select Chromecast device
        self.cast = next(
            cc for cc in chromecasts if cc.device.friendly_name == CAST_NAME)
        self.cast.wait()

    def playVideo(self):
        # get media controller
        mc = self.cast.media_controller
        # set online video url
        mc.play_media(
            'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
            'video/mp4')

        # blocks device
        mc.block_until_active()
        print(mc.status)

        # plays the video
        mc.play()
