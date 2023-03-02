import argparse
import eyed3
import logging
import os
import pathlib
import shutil

# Silence non-critical errors to eliminate warnins about bad tags
logging.getLogger("eyed3").setLevel(logging.CRITICAL)


logged_something = False

class Album:

	def __init__(self, album_path):
		self.track_details = dict()
		self.track_count = 0
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
					self.album, self.album_artist = get_album_info(mp3_path)
					self.track_count += 1
					self.album_path = album_path


	def get_track_string(self, track_num):

		if track_num is not None:
			title, bit_rate_str, length = self.track_details[track_num]

			len_m = int(length/60)
			len_s = length % 60

			return "[%s] - %2d:%02d (%2d) %s" % (bit_rate_str, len_m, len_s, int(track_num), title)
		else:
			return "[  ----  ] - xx:xx (--) ---------------------"



def get_track_details(audio_file_path):
	audio_file = eyed3.load(audio_file_path)
	tag = audio_file.tag
	info = audio_file.info
	track_num, track_count = tag.track_num
	return (track_num, tag.title, info.bit_rate_str, info.time_secs)


def get_album_info(audio_file_path):
	tag = eyed3.load(audio_file_path).tag
	return(tag.album, tag.album_artist)


def print_album(left_album, right_album):
	#want to probably do some stuff to standardize column widths and ensure
	#things won't run to the next line
	term_width = os.get_terminal_size().columns
	
	left_tracks = sorted(left_album.track_details.keys())
	right_tracks = sorted(right_album.track_details.keys())
	
	left_idx = 0
	right_idx = 0

	# Print tracks until one side is done
	while(left_idx < len(left_tracks) and right_idx < len(right_tracks)):

		left_track_str = ''
		right_track_str = ''

		left_track_num = left_tracks[left_idx]
		right_track_num = right_tracks[right_idx]

		if(left_track_num == right_track_num):
			# Print both
			left_track_str = left_album.get_track_string(left_track_num)
			left_track_str = left_track_str.ljust(int(term_width/2))
			right_track_str = right_album.get_track_string(right_track_num)
			left_idx += 1
			right_idx += 1
		
		elif left_track_num < right_track_num:
			# Only print left track
			left_track_str = left_album.get_track_string(left_track_num)
			left_track_str = left_track_str.ljust(int(term_width/2))
			right_track_str = right_album.get_track_string(None)
			left_idx += 1

		else:
			#only print right track
			left_track_str = left_album.get_track_string(None)
			left_track_str = left_track_str.ljust(int(term_width/2))
			right_track_str = right_album.get_track_string(right_track_num)
			right_idx += 1

		print(left_track_str, right_track_str)

	# Print remaining left tracks (if any)
	while left_idx < len(left_tracks):
		left_track_num = left_tracks[left_idx]
		left_track_str = left_album.get_track_string(left_track_num)
		left_track_str = left_track_str.ljust(int(term_width/2))
		right_track_str = right_album.get_track_string(None)
		left_idx += 1
		print(left_track_str, right_track_str)

	# Print remaining right tracks (if any)
	while right_idx < len(right_tracks):
		right_track_num = right_tracks[right_idx]
		left_track_str = left_album.get_track_string(None)
		left_track_str = left_track_str.ljust(int(term_width/2))
		right_track_str = right_album.get_track_string(right_track_num)
		right_idx += 1
		print(left_track_str, right_track_str)


def get_album_list(path, use_album_artist):
	albums = dict()
	for root, dirs, files in os.walk(path):
		for f in files:
			if f.lower().endswith(".mp3"):
				mp3_tag = eyed3.load(os.path.join(root, f)).tag
				album = mp3_tag.album
				
				# sometimes, album artist is empty, but artist can also have a ton of names
				# so let the user control this so they can at least compare runs with both
				if use_album_artist:
					artist = mp3_tag.album_artist
				else:
					artist = mp3_tag.artist

				if type(album) == type(None) or type(artist) == type(None):
					logging.warning("Album or Artist tags are empty for " + os.path.join(root, f))
					global logged_something
					logged_something = True
				else:
					key = album.lower().replace(" ","") + artist.lower().replace(" ","")
					if key not in albums:
						albums[key] = root
					else:
						logging.critical(os.path.join(root,f))
						logging.critical("An album already exists with key " + key)
					break

	if len(albums.keys()) > 0:
		return albums
	else:
		return None

def move_album(album, backup_dir):
	src = album.album_path
	dst = os.path.join(backup_dir, album.album_artist, album.album)
	print(src)
	print(dst)
	while(True):
		p = input("Are you sure? (y/n)")
		if p.lower() == 'n':
			return False
		elif p.lower() =='y':
			shutil.move(src, dst)
			return True


def compare_albums(left_albums, right_albums, backup_dir):
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

			#print album details
			print_album(left_album, right_album)
			print("\n\n")

			#Pause until user answers
			should_quit = False;
			while(True):
				s = input("Continue (c) : quit (q) rm left (rl) : rm right (rr)  ")
				if s.lower() == 'q':
					should_quit = True
					break
				elif s.lower() == 'c':
					break
				elif s.lower() == 'rr':
					if move_album(right_album, backup_dir):
						break
				elif s.lower() == 'rl':
					if move_album(left_album, backup_dir):
						break
					
			if should_quit:
				break

def init_argparse():
	parser = argparse.ArgumentParser(description="Try to find and list duplicate tracks between two album directories")
	parser.add_argument("left_dir", nargs="?",
			help="One of two directories to compare")
	parser.add_argument("right_dir", nargs="?",
			help="One of two directories to compare")
	parser.add_argument('-A', '--use-album-artist', dest='use_album_artist', action='store_true', help="Use album artist as part of key instead of artist")
	parser.add_argument('-l', '--log', dest='log_file', default='warnings.log', help="Logfile destination")
	parser.add_argument('-b', '--backup-dir', dest='backup_dir', default='dupes_backup', help="Backup destination")
	return parser


def main():
	parser = init_argparse()
	args = parser.parse_args()
	
	# Log important happenings to a logfile of the users choosing
	logging.basicConfig(filename=args.log_file, encoding='utf-8', filemode='w', level=logging.WARNING)

	# get the list of albums and their paths for each scan directory
	left_albums = get_album_list(args.left_dir, args.use_album_artist)
	right_albums = get_album_list(args.right_dir, args.use_album_artist)

	# Now compare them suckers
	if left_albums == type(None) or right_albums == type(None):
		print("Oops, you had some errors I don't feel like dealing with")
	else:
		compare_albums(left_albums, right_albums, args.backup_dir)

	if logged_something == True:
		print("There were warnings which were written to " + args.log_file)


if __name__ == "__main__":
		main()