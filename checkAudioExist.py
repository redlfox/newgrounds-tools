import sys, os, time, re
from pathlib import Path, PurePath
import argparse
import configparser
from utils_s import get_encoding, writeToFile, checkFileType
import filetype

# Check if audio files end with "(ID number) match audio id of Newgrounds audio artist page existing
def main() -> None:
	NGAudioArtistHtml = Path(rf"")
	with open(
	    NGAudioArtistHtml, "r", encoding=get_encoding(NGAudioArtistHtml)
	) as f:
		try:
			audioItemsFromFile = f.read()
		except Exception as e:
			# handle_caught_exception(e, known=True)
			# logger.error("检测到" + STEAM_ACCOUNT_INFO_FILE_PATH + "格式错误, 请检查配置文件格式是否正确! ")
			print(f"Failed to load json file. Error: {e}")
			sys.exit()
			return None
	# print(audioItemsFromFile)
	# print(type(audioItemsFromFile))
	newgroundsAudioItems = list(
	    re.findall(r"(?<=listen/)\d+", audioItemsFromFile)
	)
	# newgroundsAudioItems=re.findall(r"(?<=data-audio-playback\=\")\d+", audioItemsFromFile)
	print(
	    "newgroundsAudioItems length:", len(newgroundsAudioItems),
	    "newgroundsAudioItems type:", type(newgroundsAudioItems)
	)
	print("newgroundsAudioItems context:", newgroundsAudioItems)
	audioFilesDownloadedList = [
	    af
	    for af in list(Path(rf'').glob('**/*.mp3'))
	    if checkFileType(af, "mp3")
	]
	audioItemsNotDownloadedList = []
	# print(audioFilesDownloadedList[0])
	itemMatched = False
	for newgroundsAudioItem in newgroundsAudioItems:
		for audioFile in audioFilesDownloadedList:
			# Process each audio file here
			# print(f"{newgroundsAudioItem}")
			# print(rf".+ID \({newgroundsAudioItem}\).+")
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
