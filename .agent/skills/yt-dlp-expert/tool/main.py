import yt_dlp
import argparse
import sys
import os

def my_hook(d):
    if d['status'] == 'finished':
        print(f"\nDone downloading, now converting ...")
    if d['status'] == 'downloading':
        print(f"\rDownloading: {d.get('_percent_str', 'N/A')} eta: {d.get('_eta_str', 'N/A')}", end='')

class MyLogger:
    def debug(self, msg):
        # For compatibility with youtube-dl, both debug and info are passed into debug
        # You can distinguish them by the prefix '[debug] '
        if msg.startswith('[debug] '):
            pass
        else:
            self.info(msg)

    def info(self, msg):
        pass

    def warning(self, msg):
        print(f"WARNING: {msg}")

    def error(self, msg):
        print(f"ERROR: {msg}")

def get_opts(args):
    opts = {
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
        'outtmpl': '%(title)s [%(id)s].%(ext)s',
        'ignoreerrors': True, # Skip unavailable videos in playlist
    }

    # Format selection
    if args.audio_only:
        opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    elif args.format:
        opts['format'] = args.format
    else:
        # Default verified best quality
        opts['format'] = 'bv+ba/b'
        opts['merge_output_format'] = 'mp4'

    # Playlist
    if args.playlist_items:
        opts['playlist_items'] = args.playlist_items
    
    # Cookies
    if args.cookies_browser:
        opts['cookiesfrombrowser'] = (args.cookies_browser, None, None, None)
    elif args.cookies_file:
        opts['cookiefile'] = args.cookies_file

    # Network
    if args.proxy:
        opts['proxy'] = args.proxy
    
    # Subtitles
    if args.subs:
        opts.update({
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en.*', 'ja'],
            'embedsubtitles': True
        })

    # Dry run check
    if args.simulate:
        opts['simulate'] = True

    return opts

def main():
    parser = argparse.ArgumentParser(description="yt-dlp wrapper tool")
    parser.add_argument('url', help='URL to download (video or playlist)')
    parser.add_argument('--audio-only', '-a', action='store_true', help='Download audio only (mp3)')
    parser.add_argument('--format', '-f', help='Custom format selector')
    parser.add_argument('--playlist-items', '-p', help='Playlist items to download (e.g. 1,2,5-10)')
    parser.add_argument('--cookies-browser', '-cb', help='Load cookies from browser (e.g. chrome, firefox)')
    parser.add_argument('--cookies-file', '-cf', help='Load cookies from file')
    parser.add_argument('--proxy', help='Proxy URL (e.g. socks5://127.0.0.1:1080)')
    parser.add_argument('--subs', '-s', action='store_true', help='Download and embed subtitles (en, ja)')
    parser.add_argument('--simulate', action='store_true', help='Simulate download')

    args = parser.parse_args()

    opts = get_opts(args)

    print(f"Starting download for: {args.url}")
    if args.audio_only:
        print("Mode: Audio Only (MP3)")
    else:
        print("Mode: Video (Best Quality)")

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([args.url])
    except Exception as e:
        print(f"Critical Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
