# Simplified version and explanation at: https://stackoverflow.com/a/64439347/12866353

import os
import pathlib
import ffmpeg

from search_directory import search_directory, filter_video_file


def compress_all_videos(source_directory_path: str, output_directory_path: str) -> list[str]:
    files = search_directory(source_directory_path)
    video_files = filter_video_file(fileList=files)
    video_files_with_full_path = [f'{source_directory_path}/{file}' for file in video_files]
    for video_file in video_files_with_full_path:
        file_name = pathlib.Path(video_file).stem
        file_ext = pathlib.Path(video_file).suffix
        output_file_name = compress_video(
            video_full_path=video_file,
            size_upper_bound=10000,
            output_file_name=f'{output_directory_path}/{file_name}_c.{file_ext}',
        )
        print(f'Done {output_file_name}')




def compress_video(video_full_path: str, size_upper_bound: float, output_file_name: str, two_pass=True) -> str:
    """
    Compress video file to max-supported size.
    :param video_full_path: the video you want to compress.
    :param size_upper_bound: Max video size in KB.
    :param output_file_name: expected output file name
    :param two_pass: Set to True to enable two-pass encoding.
    :return: out_put_name or error
    """

    # Adjust them to meet your minimum requirements (in bps),
    # or maybe this function will refuse your video!
    total_bitrate_lower_bound = 11000
    min_audio_bitrate = 32000
    max_audio_bitrate = 256000
    min_video_bitrate = 100000

    try:
        # Bitrate reference: https://en.wikipedia.org/wiki/Bit_rate#Encoding_bit_rate
        probe = ffmpeg.probe(video_full_path)
        # Video duration, in s.
        duration = float(probe['format']['duration'])
        # Target total bitrate, in bps.
        target_total_bitrate = (
            size_upper_bound * 1024 * 8) / (1.073741824 * duration)
        if target_total_bitrate < total_bitrate_lower_bound:
            print('Bitrate is extremely low! Stop compress!')
            return None

        # Best min size, in kB.
        best_min_size = (min_audio_bitrate + min_video_bitrate) * \
            (1.073741824 * duration) / (8 * 1024)
        if size_upper_bound < best_min_size:
            print(f'Quality not good! Recommended minimum size: {
                  int(best_min_size)} KB.')
            # return False
        # Audio bitrate, in bps.
        audio_bitrate = float(next(
            (s for s in probe['streams'] if s['codec_type'] == 'audio'), None)['bit_rate'])

        # target audio bitrate, in bps
        if 10 * audio_bitrate > target_total_bitrate:
            audio_bitrate = target_total_bitrate / 10
            if audio_bitrate < min_audio_bitrate < target_total_bitrate:
                audio_bitrate = min_audio_bitrate
            elif audio_bitrate > max_audio_bitrate:
                audio_bitrate = max_audio_bitrate

        # Target video bitrate, in bps.
        video_bitrate = target_total_bitrate - audio_bitrate
        if video_bitrate < 1000:
            print(f'Bitrate {video_bitrate} is extremely low! Stop compress.')
            return None

        i = ffmpeg.input(video_full_path)
        # two_pass encoding helps produce optimized and compressed video.
        # ref: https://castr.com/blog/what-is-two-pass-encoding/
        # ffmpeg synopsis: https://ffmpeg.org/ffmpeg.html#Synopsis
        if two_pass:
            ffmpeg.output(i, os.devnull,
                          **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 1, 'f': 'mp4'}
                          ).overwrite_output().run()
            ffmpeg.output(i, output_file_name,
                          **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 2, 'c:a': 'aac', 'b:a': audio_bitrate}
                          ).overwrite_output().run()
        else:
            ffmpeg.output(i, output_file_name,
                          **{'c:v': 'libx264', 'b:v': video_bitrate, 'c:a': 'aac', 'b:a': audio_bitrate}
                          ).overwrite_output().run()

        if os.path.getsize(output_file_name) <= size_upper_bound * 1024:
            return output_file_name
        elif os.path.getsize(output_file_name) < os.path.getsize(video_full_path):  # Do it again
            return compress_video(
                video_full_path=video_full_path,
                size_upper_bound=size_upper_bound,
                output_file_name=output_file_name,
                two_pass=True,
            )
        else:
            return None
    except FileNotFoundError as e:
        print('You do not have ffmpeg installed!', e)
        print('You can install ffmpeg by reading https://github.com/kkroening/ffmpeg-python/issues/251')
        return None


if __name__ == '__main__':
    # file_name = compress_video(
    #             video_full_path='/Users/tchiu/code/playground/auto_compressor/tdir/IMG_7049.MOV',
    #             size_upper_bound=10000,
    #             output_file_name='/Users/tchiu/code/playground/auto_compressor/tdir/test.MOV',
    #             two_pass=True,
    #         )
    # print(file_name)
    compress_all_videos('/Users/tchiu/code/playground/auto_compressor/tdir', '/Users/tchiu/code/playground/auto_compressor/tdir2')
