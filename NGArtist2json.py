import orjson, sys, os, time, re
from pathlib import Path, PurePath
import argparse
from utils_s import get_encoding, readFromFile, writeToFile
from lxml import html
import shutil

def NGAudioArtistHtml2json(NGAudioArtistHtml):
	NGAudioArtistHtmlRoot = NGAudioArtistHtml.getroot()
	# print(etree.tostring(NGAudioArtistHtmlRoot))
	# print("NGAudioArtistHtml Type: ", type(NGAudioArtistHtml))
	# print("NGAudioArtistHtmlRoot Type: ", type(NGAudioArtistHtmlRoot))
	audiojson: list = [{}]
	audiojson[0]["artistNickname"] = artistNickname = NGAudioArtistHtmlRoot.cssselect(
	    "#user-header > .user-header-name > a"
	)[0].text_content().strip()
	audiojson[0]["artistNGUrl"] = artistNGUrl = NGAudioArtistHtmlRoot.cssselect(
	    "div.search > form[action*=\".newgrounds.com/audio\"]"
	)[0].get("action")
	artistId = re.match(r".+(?<=//)([^\'\"\s.\\/]+)", artistNGUrl).group(1)
	print("artistId: ", artistId)
	audiojson[0]["artistId"] = artistId
	audiojson[0]["musicPublished"]: list = []
	NGAudioArtistHtmlRootSelectionMatches = NGAudioArtistHtmlRoot.cssselect('.audio-wrapper')
	# NGAudioArtistHtmlRootSelection1stMatch=NGAudioArtistHtmlRootSelectionMatches[0]
	print("Audio count on page: ", len(NGAudioArtistHtmlRootSelectionMatches))
	for i, audioMatch in enumerate(NGAudioArtistHtmlRootSelectionMatches):
		# Match audio elements on the page.
		# print(html.tostring(audioMatch.getparent()))
		# print("audioMatch Type: ", type(audioMatch))
		audioMatchPath = NGAudioArtistHtml.getpath(audioMatch)
		# print("audioMatch Path: ", audioMatchPath)
		# print("audioMatchPath Type: ", type(audioMatchPath))
		audioMatchUrl = NGAudioArtistHtml.xpath(audioMatchPath + "/div/a")[0].get("href")
		# print("audioMatchUrl: ", audioMatchUrl)
		audioMatchID = re.match(r".+(?<=listen/)([^\'\"\s.\\/]+.*)", audioMatchUrl).group(1)
		# print("audioMatchID: ", audioMatchID)
		audiojson[0]["musicPublished"].append({})
		audioMatchIDFields = audiojson[0]["musicPublished"][-1]
		audioMatchIDFields["NGId"] = int(audioMatchID)
		audioMatchIDFields["url"] = audioMatchUrl
		audioMatchIDFields["title"] = audioMatch.cssselect(".detail-title")[0].text_content().strip()
		audioMatchIDFields["description"] = audioMatch.cssselect(".detail-description")[0].text_content().strip()
		AudioYearPath = re.sub(r"/[^/]+/[^/]+/[^/]+/[^/]+$", "", audioMatchPath, count=1)
		# print("AudioYearPath: ", AudioYearPath)
		AudioYearElement = NGAudioArtistHtml.xpath(AudioYearPath)[0]
		# print("AudioYearElement Type: ", type(AudioYearElement))
		AudioYear = AudioYearElement.get("data-attr-year")
		# print("AudioYearElement data-attr-year: ", AudioYear)
		audioMatchIDFields["yearPublished"] = int(AudioYear)
		audioMatchIDFields["NGScore"] = audioMatch.cssselect("div.item-details-meta > div.star-score"
		                                                    )[0].get("title").strip().replace("Score: ", "")
		audioMatchIDFields["type"] = audioMatch.cssselect(
		    "div.item-details > div.item-details-meta > dl > dd:nth-child(1)"
		)[0].text_content().strip()
		audioMatchIDFields["genre"] = audioMatch.cssselect(
		    "div.item-details > div.item-details-meta > dl > dd:nth-child(2)"
		)[0].text_content().strip()
		audioMatchIDFields["NGViews"] = int(
		    audioMatch.cssselect("div.item-details > div.item-details-meta > dl > dd:nth-child(3)")
		    [0].text_content().strip().replace(" Views", "").replace(",", "")
		)
		# print("audiojson: ", audiojson)
		# sys.exit()
	return audiojson

def main() -> None:
	parser = argparse.ArgumentParser(description="Tool to extract metadata from Newgrounds audio artist pages.")
	parser.add_argument(
	    "-jl", "-json-file-list", default=None, help="Write generated Newgrounds JSON paths to the givien file."
	)
	parser.add_argument("-hl", "-html-file-list", default=None, help="List of HTML file paths in a file to process.")
	parser.add_argument("-m", "-move-html", default=None, help="Move HTML files to a location.")
	parser.add_argument("-ad", default=None, help="test.")
	args = parser.parse_args()
	NGAudioArtistHtmlFilelist = []
	if args.hl:
		try:
			NGAudioArtistHtmlFilelist = readFromFile(args.hl).splitlines()
		except Exception as e:
			sys.exit("Failed to read html file list, will exit.")
	else:
		parser.print_help()
	if not NGAudioArtistHtmlFilelist:
		sys.exit("No html to process, will exit.")
	autoMoveHtml = False
	if args.m:
		autoMoveHtml = PurePath(args.m)
	if args.ad:
		jsonDest = args.ad
	else:
		parser.print_help()
		sys.exit("No json destination, will exit.")

	for NGAudioArtistHtmlFile in NGAudioArtistHtmlFilelist:
		NGAudioArtistHtmlFile = Path(NGAudioArtistHtmlFile)
		NGAudioArtistHtml = html.parse(NGAudioArtistHtmlFile)
		audiojson = NGAudioArtistHtml2json(NGAudioArtistHtml)
		# print(html.tostring(NGAudioArtistHtml),"\nNGAudioArtistHtml Type: ", type(NGAudioArtistHtml))
		writeToFile(
		    rf"{jsonDest}\{NGAudioArtistHtmlFile.stem}.json",
		    orjson.dumps(audiojson, option=orjson.OPT_INDENT_2).decode('utf-8'), openmode='w', file_encoding='utf-8'
		)
		if args.jl:
			try:
				writeToFile(
				    Path(args.jl), rf"{jsonDest}\{NGAudioArtistHtmlFile.stem}.json", openmode='a', file_encoding='utf-8'
				)
			except Exception as e:
				print("Failed to write json file paths to ", args.jl)
				sys.exit()
		if autoMoveHtml:
			print("Moving ", NGAudioArtistHtmlFile, " to new location.")
			shutil.copy2(NGAudioArtistHtmlFile, autoMoveHtml / NGAudioArtistHtmlFile.name)

if __name__ == "__main__":
	main()
