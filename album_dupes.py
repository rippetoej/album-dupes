import argparse
import eyed3
import logging
import os
import pathlib

# Silence non-critical errors to eliminate warnins about bad tags
logging.getLogger("eyed3").setLevel(logging.CRITICAL)


class Album:

	def __init__(self, album_path):
		self.track_details = dict()
		for root, dirs, files in os.walk(album_path):
			for f in files:
				if f.lower().endswith(".mp3"):
					mp3_path = os.path.join(root, f)
					track_num, title, bit_rate_str, time_secs = get_track_details(mp3_path)
					
					# For files that don't have a track number, assign one with a high value
					if track_num is None:
						# do a quick search to make sure you don't reassign a track number 
						# in case you have multiple unnumbered tracks
						start_num = 9999
						while start_num in self.track_details.keys():
							start_num = start_num - 1

						track_num = start_num

					self.track_details[track_num] = (title, bit_rate_str, time_secs)
					self.album, self.album_artist, self.track_count = get_album_info(mp3_path)


	def get_track_string(self, track_num):
		title, bit_rate_str, length = self.track_details[track_num]

		len_m = int(length/60)
		len_s = length % 60

		return "[%s] - %2d:%02d (%s) %s" % (bit_rate_str, len_m, len_s, track_num, title)



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


def print_album(left_album, right_album):
	#want to probably do some stuff to standardize column widths and ensure
	#things won't run to the next line
	term_width = os.get_terminal_size().columns
	
	left_tracks = sorted(left_album.track_details.keys())
	
	# print each duplicate track in both columns, unmatched tracks in their respective columns	
	for track_num in left_tracks:
		left_track_str = left_album.get_track_string(track_num)
		left_track_str = left_track_str.ljust(int(term_width/2))
		if track_num in right_album.track_details:
			right_track_str = right_album.get_track_string(track_num)
			print(left_track_str, right_track_str)


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

	left_album_total = len(left_albums.keys())
	left_album_count = 0

	for album_key in left_albums:
		left_album_count = left_album_count + 1

		if album_key in right_albums:
			
			#build dicts with track details
			left_album = Album(left_albums[album_key])
			right_album = Album(right_albums[album_key])

			#print header
			str = ""
			print(str.ljust(term_width, '='))
			print("%d/%d" % (left_album_count, left_album_total))

			left_path = ("%s" % left_albums[album_key]).center(int(term_width/2))
			right_path = ("%s" % right_albums[album_key]).center(int(term_width/2))
			print(left_path, right_path)

			#print track details
			print_album(left_album, right_album)
			print("\n\n")



def init_argparse():
	parser = argparse.ArgumentParser(description="Try to find and list duplicate tracks between two album directories")
	parser.add_argument("left_dir", nargs="?",
			help="One of two directories to compare")
	parser.add_argument("right_dir", nargs="?",
			help="One of two directories to compare")
	return parser


def main():
	parser = init_argparse()
	args = parser.parse_args()
	
	left_albums = get_album_list(args.left_dir)
	right_albums = get_album_list(args.right_dir)

	compare_albums(left_albums, right_albums)


if __name__ == "__main__":
		main()