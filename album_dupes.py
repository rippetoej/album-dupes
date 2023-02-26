import argparse
import eyed3
import os
import pathlib
	

def init_argparse():
		parser.add_argument("left_dir", nargs="?",
				help="One of two directories to compare")
		parser.add_argument("right_dir", nargs="?",
				help="One of two directories to compare")
		return parser

def get_track_details(audio_file_path):
	audio_file = eyed3.load(audio_file_path)
	tag = audio_file.tag
	info = audio_file.info
	track_num, track_count = tag.track_num
	return (track_num, tag.title, info.bit_rate_str)

def print_tag_info(audio_file_path):
	audio_file = eyed3.load(audio_file_path)
	tag = audio_file.tag
	info = audio_file.info

	artist = tag.artist
	# format name only if only standard chars (don't want to rename V▲LH▲LL)
	if re.match(r'^[ a-zA-Z0-9_-]+$', artist):
		artist = artist.title()

	album = tag.album
	title = tag.title
	track_num, track_count = tag.track_num

	bitrate = info.bit_rate_str
	print(track_num, " ", title, " -- ", artist, " -- ", album, "[", bitrate, "]")

def print_album_info(album_path):
	print(album_path)
	for root, dirs, files in os.walk(album_path):
		for f in files:
			if f.lower().endswith(".mp3"):
				print_tag_info(os.path.join(root, f))

def build_album_dict(album_path):
	album_dict = dict()
	for root, dirs, files in os.walk(album_path):
		for f in files:
			if f.lower().endswith(".mp3"):
				track_num, title, bit_rate_str = get_track_details(os.path.join(root, f))
				album_dict[track_num] = (title, bit_rate_str)
	return album_dict

def print_albums(left_album, right_album):
	term_width = os.get_terminal_size().columns
	#want to probably do some stuff to standardize column widths and ensure
	#things won't run to the next line
	

def main():
	parser = init_argparse()
	args = parser.parse_args()
	
	left_album = build_album_dict(args.left_dir)
	right_album = build_album_dict(args.right_dir)

	# artists = os.listdir(args.left_dir)

	# d = dict()

	# for root, dirs, folders in os.walk(args.left_dir):
	#   print(root)
	#   dname = os.path.basename(root)
	#   if dname in artists:
	#     print("found an artist: ", dname)
	#     d[dname] = root

	# print(d)


if __name__ == "__main__":
		main()