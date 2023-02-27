import argparse
import eyed3
import os
import pathlib



# walk left dir, get all albums with path (from mp3)
# walk right directory and check  against albums in left dir
# if there is a match read in all tracks and store them in a dict, keyed by track number for both left and right
#


class Album:
	def __init__(self, album_path):
		self.track_details = dict()
		for root, dirs, files in os.walk(album_path):
			for f in files:
				if f.lower().endswith(".mp3"):
					mp3_path = os.path.join(root, f)
					track_num, title, bit_rate_str, time_secs = get_track_details(mp3_path)
					self.track_details[track_num] = (title, bit_rate_str, time_secs)
					self.album, self.album_artist, self.track_count = get_album_info(mp3_path)

	def get_track_string(self, track_num):
		title, bit_rate_str, length = self.track_details[track_num]

		len_m = int(length/60)
		len_s = length % 60

		return "[%s] - %2d:%02d (%s) %s" % (bit_rate_str, len_m, len_s, track_num, title)




def init_argparse():
	parser = argparse.ArgumentParser(description="Try to find and list duplicate tracks between two album directories")
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
	return (track_num, tag.title, info.bit_rate_str, info.time_secs)

def get_album_info(audio_file_path):
	tag = eyed3.load(audio_file_path).tag
	track_num, track_count = tag.track_num
	return(tag.album, tag.album_artist, track_count)

def print_tag_info(audio_file_path):
	audio_file = eyed3.load(audio_file_path)
	tag = audio_file.tag
	info = audio_file.info

	artist = tag.artist
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


def print_album(left_album, right_album):
	#want to probably do some stuff to standardize column widths and ensure
	#things won't run to the next line
	term_width = os.get_terminal_size().columns
	
	left_keys = sorted(left_album.track_details.keys())

	for key in left_keys:
		left_column = left_album.get_track_string(key)
		left_column = left_column.ljust(int(term_width/2))
		if key in right_album.track_details:
			right_column = left_album.get_track_string(key)
			print(left_column, right_column)

def get_album_list(path,):
	albums = dict()
	for root, dirs, files in os.walk(path):
		for f in files:
			if f.lower().endswith(".mp3"):
				mp3_tag = eyed3.load(os.path.join(root, f)).tag
				albums[mp3_tag.album] = root
				break

	return albums


def compare_albums(left_albums, right_albums):
	term_width = os.get_terminal_size().columns

	for album_key in left_albums:
		if album_key in right_albums:
			
			#build dicts with track details
			left_album = Album(left_albums[album_key])
			right_album = Album(right_albums[album_key])

			#print header
			str = ""
			print(str.ljust(term_width, '='))
			left_path = ("%s" % left_albums[album_key]).center(int(term_width/2))
			right_path = ("%s" % right_albums[album_key]).center(int(term_width/2))
			print(left_path, right_path)

			#print track details
			print_album(left_album, right_album)
			print("\n\n")

def main():
	parser = init_argparse()
	args = parser.parse_args()
	
	left_albums = get_album_list(args.left_dir)
	right_albums = get_album_list(args.right_dir)
	compare_albums(left_albums, right_albums)

if __name__ == "__main__":
		main()