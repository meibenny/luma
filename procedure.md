# Converting Videos from .MOV to .MP4

See [stackoverflow][1]

```
ffmpeg -i {in-video}.mov -vcodec h264 -acodec aac {out-video}.mp4
```

I am using Windows 10 with ffmpeg version 

```
ffmpeg version git-2020-02-09-5ad1c1a
```

```
C:\Users\ben>ffmpeg --help
ffmpeg version git-2020-02-09-5ad1c1a Copyright (c) 2000-2020 the FFmpeg developers
  built with gcc 9.2.1 (GCC) 20200122
  configuration: --enable-gpl --enable-version3 --enable-sdl2 --enable-fontconfig --enable-gnutls --enable-iconv --enable-libass --enable-libdav1d --enable-libbluray --enable-libfreetype --enable-libmp3lame --enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libopenjpeg --enable-libopus --enable-libshine --enable-libsnappy --enable-libsoxr --enable-libtheora --enable-libtwolame --enable-libvpx --enable-libwavpack --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxml2 --enable-libzimg --enable-lzma --enable-zlib --enable-gmp --enable-libvidstab --enable-libvorbis --enable-libvo-amrwbenc --enable-libmysofa --enable-libspeex --enable-libxvid --enable-libaom --enable-libmfx --enable-ffnvcodec --enable-cuvid --enable-d3d11va --enable-nvenc --enable-nvdec --enable-dxva2 --enable-avisynth --enable-libopenmpt --enable-amf
  libavutil      56. 39.100 / 56. 39.100
  libavcodec     58. 68.100 / 58. 68.100
  libavformat    58. 38.100 / 58. 38.100
  libavdevice    58.  9.103 / 58.  9.103
  libavfilter     7. 75.100 /  7. 75.100
  libswscale      5.  6.100 /  5.  6.100
  libswresample   3.  6.100 /  3.  6.100
  libpostproc    55.  6.100 / 55.  6.100
Hyper fast Audio and Video encoder
usage: ffmpeg [options] [[infile options] -i infile]... {[outfile options] outfile}...

Getting help:
    -h      -- print basic options
    -h long -- print more options
    -h full -- print all options (including all format and codec specific options, very long)
    -h type=name -- print all options for the named decoder/encoder/demuxer/muxer/filter/bsf/protocol
    See man ffmpeg for detailed description of the options.
```

[1]: https://superuser.com/questions/1155186/convert-mov-video-to-mp4-with-ffmpeg
