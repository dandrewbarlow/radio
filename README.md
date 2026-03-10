# radio.sh

Written by Andrew Barlow ([github](https://github.com/dandrewbarlow) | [website](https://a-barlow.com))

## Description

A simple CLI internet radio interface for old internet fans. Requires `fzf`,
`cvlc`, and `curl`.

### Goals

This project was written because of my fondness for old internet ideas that
have gone out of fashion. Internet radio is one of those cool-in-theory ideas
that has a bunch of hurdles in the way of the actual experience. GUIs are old
and outdated, station lists are pulled from weird sources, editing your saved
stations can result in menu hell, internet services require accounts and try to
upcharge you every step of the way.

I wanted a radio player within the terminal, I wanted to choose and organize my
radio stations myself in a plaintext file that I could work my vim-fu on, and I
didn't want to see ads or get emails about my radio player. There are more
feature-rich clients available, but if you just want to play some dang music
while you're coding give this script a shot.

### About

This script leans on `VLC` for streaming and `fzf` for its easy terminal
interface. The result is lean and powerful: a simple, highly functional internet
radio player for terminal power users. I'm sure there are many like it, but this
one is mine.

## Install Dependencies

Install [fzf](https://github.com/junegunn/fzf) and
[VLC](https://www.videolan.org/vlc/) for your platform of choice.
`curl` is included in most Unix-like systems by default.

## Usage

Place all internet radio stream URLs in a file called `config.txt` within the
project directory. To include a station name, precede the URL with a comment:

```
# Station Name
https://station-url.com
```

Extraneous comments will not be parsed, but any line starting with `http` will
search the line above it for a commented name. If none is found, it will
default to the stream URL.

Run the script:

```
./radio.sh
```

Or make a shell alias so your tunes are never far away:

```
alias radio='/path/to/radio.sh'
```

### Tips

Station selection uses fzf, a fuzzy finder — type any part of a station name
to filter. Consider adding genre tags or other keywords to station names in
your config to make searching faster.

### Station Recs

You gotta find the stream URLs for yourself. This is the blessing/curse of this
design, but there are many great resources out there.

For those that need somewhere to start:

* Collections
    * [Soma FM](https://somafm.com/): ad free, and diverse selection of stations
    * [RadioBrowser](https://www.radio-browser.info/): FOSS database of
      stations. Their browsing categories are not great for finding stuff
      without digging around imo, but if you know what you're looking for it's
      a great tool to find stream URLs.
    * [BBC
      Stations](https://en.everybodywiki.com/List_of_BBC_radio_stream_URLs):
      something for everybody
* Individual Stations (matters of taste, obvs)
    * [KEXP](https://www.kexp.org/): the GOAT. Their [streaming URLs are hidden
      without some googling, though](https://www.kexp.org/streaming-urls/)
    * [Triple J](https://www.abc.net.au/triplej): another GOAT. See [direct
      streams
      here](https://help.abc.net.au/hc/en-us/articles/4402927208079-Where-can-I-find-direct-stream-URLs-for-ABC-Radio-stations-)
      or [time-delayed streams
      here](https://www.abc.net.au/triplej/time-delayed-streams/9445252)
* Other ideas
    * Google for some local stations. Find the nearest college radio and tune in.

## Limitations

In a perfect world, I would be able to show some additional metadata about the
songs now playing, but a cursory look into the possibility discouraged me. Too
many stream formats/codecs, hardly any standardization. VLC can parse some
basic information, but it's usually basically worthless as metadata. You gotta
pick your battles.

One of the factors you can't get around is stream bitrate tradeoffs. The onus
is on the user to find streams that can play well over their internet
connection. One likes to hope that's not an issue these days, and one is often
wrong.

Volume controls are another thing that the user has to do themselves — at a
hardware level, a software mixer, whatever. This script embraces the live
ethos of radio with the bold and innovative decision to have no playback
controls. It's either playing or it's not.

For minimalism's sake, VLC's output is suppressed. This also means if something
goes wrong, it will not tell you. A safe troubleshooting guide is to double
check that the URL is correct and can be listened to with VLC outside of this
script:

```
cvlc https://stream-url.com
```
