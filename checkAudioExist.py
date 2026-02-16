import sys, os, time, re
from pathlib import Path, PurePath
import argparse
import configparser
from utils_s import get_encoding, writeToFile, checkFileType
import filetype

# Check if audio files end with "(ID number) match audio id of Newgrounds audio artist page existing
def main() -> None:
	parser = argparse.ArgumentParser(description="Tool to check if Newgrounds audio files extracted from a file contains their urls exist.")
	parser.add_argument("-ef", default=None, help="Specifies the file to extract Newgrounds audio urls.")
	parser.add_argument("-ad", default=None, help="Specifies the directory to match mp3 files.")
	args = parser.parse_args()
	if not args.ef or not args.ad:
		parser.print_help()
		sys.exit() 
	audioDownloadDir=Path(args.ad)
	NGAudioArtistHtml = Path(args.ef)
	with open(NGAudioArtistHtml, "r", encoding=get_encoding(NGAudioArtistHtml)) as f:
		try:
			audioItemsFromFile = f.read()
		except Exception as e:
			print(f"Failed to load json file. Error: {e}")
			sys.exit()
			return None

	newgroundsAudioItems = list(re.findall(r"(?<=listen/)\d+", audioItemsFromFile))
	# newgroundsAudioItems=re.findall(r"(?<=data-audio-playback\=\")\d+", audioItemsFromFile)
	print("newgroundsAudioItems length:", len(newgroundsAudioItems))
	print("newgroundsAudioItems context:", newgroundsAudioItems)
	# Get mp3 files in the directory.
	audioFilesDownloadedList = [af for af in list(audioDownloadDir.glob('**/*.mp3')) if checkFileType(af, "mp3")]
	audioItemsNotDownloadedList = []
	itemMatched = False

	for newgroundsAudioItem in newgroundsAudioItems:
		for audioFile in audioFilesDownloadedList:
			# Process each audio file here
			if re.match(rf".+\(ID {newgroundsAudioItem}\).+", str(audioFile)):
				print("Found match:", newgroundsAudioItem, audioFile)
				itemMatched = True
				break
		else:
			print("No match found for:", newgroundsAudioItem)
			audioItemsNotDownloadedList.append(newgroundsAudioItem)
		if itemMatched:
			itemMatched = False
			continue
	print(audioItemsNotDownloadedList)

if __name__ == "__main__":
	main()
