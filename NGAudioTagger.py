import orjson, sys, os, time, re
from pathlib import Path, PurePath
import argparse
import configparser
from utils_s import get_encoding, writeToFile, readFromFile, checkFileType
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TRCK, COMM, TXXX, TORY, TOR, TYER, TYE, TCON
from mutagen.easyid3 import EasyID3
from NGArtist2json import NGAudioArtistHtml2json
import filetype

def NGAudioTagEditor(
    mp3FilePath: Path, NGJSONData: dict = None, KeepValidYear: bool = True, KeepValidTitle: bool = True,
    KeepValidArtist: bool = True, KeepNGAPAlbum: bool = True, KeepOrigComment: bool = True,
    albumName: str = "Newgrounds Audio Portal", fuzzyMatch: bool = False
):
	fileEdited = False
	try:
		mp3file = MP3(mp3FilePath)
		Id3file = ID3(mp3FilePath, v2_version=3)
		Id3filev24 = ID3(mp3FilePath)
	except Exception as e:
		print(f"Can't read ID3v2 tag from file. Error: {e}")
		fileFailedtoEditTags = mp3FilePath
		return fileFailedtoEditTags
	artistMatched = False
	audioItemMatched = False
	fileFailedtoEditTags = ""
	Id3fileYearv23Text = "0"
	Id3fileYearv24Text = ""
	Id3fileTitleText = ""
	Id3fileArtistText = ""
	Id3fileDescriptionText = ""
	Id3fileNGTypeText = ""
	Id3fileGenreText = ""
	Id3fileNGScoreText = ""
	Id3fileNGViewsText = ""
	Id3fileCommentText = ""
	Id3fileAlbumText = ""
	Id3fileTrackText = ""
	try:
		Id3fileYearv23Text = Id3file["TYER"].text[0]
	except:
		pass
	try:
		Id3fileYearv24Text = Id3filev24["TYER"].text[0]
	except:
		pass
	if not Id3fileYearv23Text:
		if not Id3fileYearv24Text:
			pass
		else:
			Id3fileYearv23Text = Id3fileYearv24Text
	try:
		Id3fileTitleText = Id3file["TIT2"].text[0]
	except Exception as e:
		pass
	try:
		Id3fileArtistText = Id3file["TPE1"].text[0]
	except Exception as e:
		pass
	try:
		Id3fileDescriptionText = Id3file["TXXX:DESCRIPTION"].text[0]
	except:
		pass
	try:
		Id3fileCommentText = Id3file["COMM::eng"].text[0]
	except:
		pass
	try:
		Id3fileNGTypeText = Id3file["TXXX:NGTYPE"].text[0]
	except:
		pass
	try:
		Id3fileGenreText = Id3file["TCON"].text[0]
	except:
		pass
	try:
		Id3fileNGScoreText = Id3file["TXXX:NGSCORE"].text[0]
	except:
		pass
	try:
		Id3fileNGViewsText = Id3file["TXXX:NGVIEWS"].text[0]
	except:
		pass
	print(Id3fileArtistText)

	try:
		NGID = int(re.match(r".+(((?<=sub\=)|(?<=listen/))\d+).*", Id3fileCommentText).group(1))
		print("NGID from comment: ", NGID)
	except:
		NGID = None
	if not NGID:
		try:
			NGID = int(re.match(r".+\(ID: (\d+)\)$", Id3fileTitleText).group(1))
			print("NGID from title: ", NGID)
		except:
			NGID = None
	if not NGID and fuzzyMatch:
		# print("asd")
		try:
			NGID = int(re.match(r"^(\d+)_.+", PurePath(mp3FilePath).stem).group(1))
			print("NGID from filename with fuzzy match: ", NGID)
		except:
			NGID = None
	if NGID and NGJSONData:
		print("Filling tags from NGJSONData for ", mp3FilePath)
		try:
			for artistInfo in NGJSONData:
				print("artist nickname: ", artistInfo["artistNickname"])
				if Id3fileArtistText.casefold() == artistInfo["artistNickname"].casefold():
					print("Matched artist nickname: ", artistInfo["artistNickname"])
					artistMatched = artistInfo
					break
			if artistMatched:
				for audioId in artistMatched["musicPublished"]:
					audioData = audioId
					# print("fasdfd: ", audioId, " ", NGID)
					if NGID == int(audioData["NGId"]):
						print("Matched audio ID: ", NGID)
						audioItemMatched = audioData
						break
			else:
				for artistInfo in NGJSONData:
					for audioId in artistInfo["musicPublished"]:
						audioData = audioId
						# print("fasdfd: ", audioId, " ", NGID)
						if NGID == int(audioData["NGId"]):
							print("Matched audio ID without artist match: ", NGID)
							artistMatched = artistInfo
							audioItemMatched = audioData
							break
					if audioItemMatched:
						break
			if audioItemMatched:
				# Fill tags here
				if re.match(r"\s*", Id3fileTitleText) or not Id3fileTitleText or not KeepValidTitle:
					print("Filling title tag")
					if not Id3fileTitleText:
						Id3fileTitleEncoding = 1
					else:
						Id3fileTitleEncoding = Id3file["TIT2"].encoding
					Id3file["TIT2"] = TIT2(
					    encoding=Id3fileTitleEncoding, text=audioItemMatched["title"] + " (ID: " + str(NGID) + ")"
					)
				if re.match(r"\s*", Id3fileArtistText) or not Id3fileArtistText or not KeepValidArtist:
					print("Filling artist tag")
					if not Id3fileArtistText:
						Id3fileArtistEncoding = 1
					else:
						Id3fileArtistEncoding = Id3file["TPE1"].encoding
					Id3file["TPE1"] = TPE1(encoding=Id3fileArtistEncoding, text=artistMatched["artistNickname"])
				if not 2003 <= int(Id3fileYearv23Text) < 2100 or not Id3fileYearv23Text or not KeepValidYear:
					print("Filling year tag")
					Id3file["TYER"] = TYER(encoding=3, text=str(audioItemMatched["yearPublished"]))
				if not audioItemMatched["description"] in Id3fileDescriptionText or not Id3fileDescriptionText:
					print("Filling description tag")
					Id3file["TXXX"] = TXXX(encoding=3, desc="DESCRIPTION", text=audioItemMatched["description"])
					Id3file.save(v2_version=3)
					Id3file = ID3(mp3FilePath, v2_version=3)
				Id3file["TXXX"] = TXXX(encoding=3, desc="NGTYPE", text=audioItemMatched["type"])
				if re.match(r"\s*", Id3fileCommentText) or not Id3fileCommentText or not KeepOrigComment:
					print("Filling comment tag")
					if not Id3fileCommentText:
						Id3fileCommentEncoding = 1
					else:
						Id3fileCommentEncoding = Id3file["COMM::eng"].encoding
					Id3file["COMM"] = COMM(
					    encoding=Id3fileCommentEncoding, lang="eng", desc="",
					    text="This track can be found at: " + audioItemMatched["url"]
					)
				Id3file.save(v2_version=3)
				Id3file = ID3(mp3FilePath, v2_version=3)
				Id3file["TCON"] = TCON(encoding=3, text=audioItemMatched["genre"])
				Id3file["TXXX"] = TXXX(encoding=3, desc="NGSCORE", text=audioItemMatched["NGScore"])
				Id3file.save(v2_version=3)
				Id3file = ID3(mp3FilePath, v2_version=3)
				Id3file["TXXX"] = TXXX(encoding=3, desc="NGVIEWS", text=str(audioItemMatched["NGViews"]))
				Id3file.save(v2_version=3)
				Id3file = ID3(mp3FilePath, v2_version=3)
				if not Id3fileAlbumText or not KeepNGAPAlbum:
					print("Filling album tag")
					if not Id3fileAlbumText:
						Id3fileAlbumEncoding = 1
					else:
						Id3fileAlbumEncoding = Id3file["TALB"].encoding
					Id3file["TALB"] = TALB(encoding=Id3fileAlbumEncoding, text=albumName)
				fileEdited = True
				# sys.exit()
				# if not KeepValidTitle or not re.match(
				#     r".+\(ID: \d+\).*", Id3file["TIT2"].text[0]
				# ):
				# 	pass
			else:
				print("No audio item match found for ID ", NGID, " in NGJSONData")
				fileFailedtoEditTags = mp3FilePath
		except Exception as e:
			print(f"Failed to fill tags from NGJSONData. Error: {e}")
			fileFailedtoEditTags = mp3FilePath
		pass
	elif not NGID and NGJSONData:
		print("No ID match found in comment for ", mp3FilePath)
	# sys.exit()
	# Id3fileTitle = Id3file["TIT2"]
	if Id3file.get("TIT2"):
		Id3fileTitleText = Id3file.get("TIT2").text[0]
		if re.match(r".+\(ID: \d+\).*", Id3fileTitleText):
			print("Matched ID in title for ", mp3FilePath, ", nothing to do.")
			if fileEdited:
				Id3file.save(v2_version=3)
		else:
			print("Missing ID in title for ", mp3FilePath)
			if NGID:
				print("Matched ID in comment: ", NGID, " for ", mp3FilePath)
				Id3file["TIT2"] = TIT2(
				    encoding=Id3file["TIT2"].encoding, text=Id3fileTitleText + " (ID: " + str(NGID) + ")"
				)
				Id3file.save(v2_version=3)
				print("Edited file's title metadata to contain ID and saved: ", mp3FilePath)
			else:
				print("No ID match found in comment for ", mp3FilePath)
				if not fileFailedtoEditTags:
					fileFailedtoEditTags = mp3FilePath
				if fileEdited:
					Id3file.save(v2_version=3)
	else:
		print("No title tag in ", mp3FilePath)
		fileFailedtoEditTags = mp3FilePath

	return fileFailedtoEditTags

def NGAudioRenamer(mp3FilePath: Path, aliasesJson: list):

	try:
		Id3file = ID3(mp3FilePath)
	except Exception as e:
		print(f"Can't read ID3v2 tag from file. Error: {e}")
		fileFailedtoRename = mp3FilePath
		return fileFailedtoRename
	aliasNames = []
	mp3FileExceptNamePattern = ""
	artistValidFilename = ""
	titleValidFilename = ""
	fileFailedtoRename = ""
	artistExists = Id3file.get("TPE1")
	titleExists = Id3file.get("TIT2")
	if not artistExists or not titleExists:
		print("Missing artist or title tag for ", mp3FilePath)
		fileFailedtoRename = mp3FilePath
		return fileFailedtoRename
	if aliasesJson:
		for artistInfo in aliasesJson:
			artistInfoAlias = artistInfo.get("artistAliases")
			if artistInfoAlias:
				artistInfoNames = [artistInfo["artistNickname"], *artistInfo["artistNickname"]]
				for artistName in artistInfoNames:
					if artistExists.text[0].casefold() == artistName.casefold():
						artistNames = artistInfoNames
						break
				if artistNames:
					break
			else:
				continue
	artistValidFilename = re.sub("\\/", "-", re.sub(r"[:*?\"<>|]", "", Id3file["TPE1"].text[0]))
	titleValidFilename = re.sub("\\/", "-", re.sub(r"[\\/:*?\"<>|]", "", Id3file["TIT2"].text[0]))
	if re.match(f"{artistValidFilename} - .+", titleValidFilename):
		mp3FileExceptName = titleValidFilename + ".mp3"
	elif artistValidFilename and titleValidFilename:
		mp3FileExceptName = artistValidFilename + " - " + titleValidFilename + ".mp3"
	# if re.match(mp3FileExceptNamePattern,PurePath(mp3FilePath).stem):
	if PurePath(mp3FilePath).stem != re.sub(r"\.mp3$", "", mp3FileExceptName):
		print("File name does not match metadata title and artist for ", mp3FilePath)
		newMp3FilePath: Path = Path(PurePath(mp3FilePath).parent / mp3FileExceptName)
		if newMp3FilePath.exists():
			print("Target file name already exists: ", newMp3FilePath)
			return
		mp3FilePath.rename(newMp3FilePath)
		print("Renamed file to: ", newMp3FilePath)

def main() -> None:

	# init()
	parser = argparse.ArgumentParser(description="Tool to edit Newgrounds audio's tags.")
	parser.add_argument("-f", "-fuzzy-match", action="store_true", help="Optional, test")
	parser.add_argument("-jl", "-json-file-list", default=None, help="Read Newgrounds JSON paths from the givien file.")
	parser.add_argument("-a", "-alias-json", default=None, help="JSON file that storage artists' alias names.")
	parser.add_argument("-ngapl", default=None, help="test.")
	args = parser.parse_args()
	if args.f:
		fuzzyMatch = True
		print("Fuzzy match enabled.")
	else:
		fuzzyMatch = False
	if args.jl:
		try:
			NGAudioArtistHtmlFilelist = readFromFile(args.jl).splitlines()
		except Exception as e:
			print("Failed to load json file paths from ", args.jl)
			sys.exit()
	aliasJson = []
	if args.a:
		try:
			aliasJson = orjson.loads(readFromFile(args.a))
		except Exception as e:
			print("Failed to load artist alias json from ", args.a)

	for countIndex, NGAudioArtistHtmlFileItem in enumerate(NGAudioArtistHtmlFilelist, start=1):
		if Path(NGAudioArtistHtmlFileItem).is_file() is False:
			print("File does not exist: ", NGAudioArtistHtmlFileItem)
			continue
		with open(NGAudioArtistHtmlFileItem, "r", encoding="utf-8") as f:
			try:
				NGJSONDataPart = orjson.loads(f.read())
			except Exception as e:
				# handle_caught_exception(e, known=True)
				print(f"Failed to load json file. Error: {e}")
				sys.exit()
				return None
		if countIndex == 1:
			print("Extending NGJSONData with data from ", NGAudioArtistHtmlFileItem)
			NGJSONData = NGJSONDataPart
			continue
		else:
			print("Extending NGJSONData with data from ", NGAudioArtistHtmlFileItem)
			NGJSONData.extend(NGJSONDataPart)

	print("Loaded NGJSONData with ", len(NGJSONData), " artists' data.")
	# sys.exit()
	fileFailedtoEditTags = ""
	filesFailedtoEditTags = []
	fileFailedtoRename = ""
	filesFailedtoRename = []
	with open(args.ngapl, "r", encoding="utf-8") as f:
		for file in f.read().splitlines():
			# file = file.strip()
			if Path(file).is_file() is False:
				print("File does not exist: ", file)
				continue
			if not checkFileType(file, "mp3"):
				continue
			print("Processing file: ", file)
			# continue
			mp3FilePath = Path(file)
			fileFailedtoEditTags = NGAudioTagEditor(mp3FilePath, NGJSONData, fuzzyMatch=fuzzyMatch)
			if fileFailedtoEditTags:
				filesFailedtoEditTags.append(fileFailedtoEditTags)
			fileFailedtoRename = NGAudioRenamer(mp3FilePath, aliasesJson=aliasJson)
			if fileFailedtoRename:
				filesFailedtoRename.append(fileFailedtoRename)

	print("Files failed to edit tags: ", filesFailedtoEditTags, "\nFiles failed to rename: ", filesFailedtoRename)
