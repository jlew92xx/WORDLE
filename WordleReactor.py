import re
import ChatBot
GREEN = "🟩"
YELLOW = "🟨"
WHITE = "⬜"
BLACK = "⬛"
# Yeah I know this is stupid but too lazy to change it.
GREENREACT = GREEN
YELLOWREACT = YELLOW
WHITEREACT = WHITE
BLACKREACT = BLACK
reactDict = {"1": ["🤔"],
             "2": ["🚂"],
             "3": ["👏", "🏀"],
             "4": ["🏌️‍♀️"],
             "5": ["👍"],
             "6": ["😱"],
             "X": ["🪦"]}

regStatement = "Wordle \d*\s([1-6]|X|⛈️)/6"


def getReactions(rawMsg: list):

    i = 0
    header = ""
    for line in rawMsg:
        #For some reason, NYTs decided to add a comma in their puzzle number we must replace it.
        line = line.replace(',', '')
        
        
        if (re.search(regStatement, line)):
            header = line
            rawMsg[i] = line
            break
        i += 1
    if (header == ""):
        return None

    output = []

    results = []
    for line in rawMsg:
        if (re.search("(" + GREEN + "|" + YELLOW + "|" + WHITE + "|" + BLACK + "){5}", line)):
            results.append(line)

    scoreList = header.split()
    copyList = list.copy(scoreList)
    for word in copyList:
        if "Wordle" in word:
            break
        else:
            scoreList.pop(0)

    score = scoreList[2][0]
    #comparing emoji is too tricky. but 9928 is the storm cloud
    isWinner = not(score == "X" or ord(score) == 9928)

    if not isWinner:
        siz = 6
        score = "X"
        botReact = ChatBot.giveResponse("give me 5 emojis to react to a losing wordle score on discord. just the emojis nothing else. DO NOT NUMBER THEM. DO NOT TO PUT THEM ON DIFFERENT LINES. I just want five emoji one one line next each other with nothing between.", "poop")
        print(botReact)
        if botReact != "poop":
            output.extend(list(botReact))
            output = list(filter(None, output))
    else:
        try:
            siz = int(score)
        except:
            return None
    if siz != len(results):
        return None

    if (score in reactDict.keys()):
        listReact = reactDict[score]
        for R in listReact:
            output.append(R)

    winLine = GREEN * 5

    if isWinner:
        lastLine = results.pop()
        if lastLine != winLine:
            return None

    else:
        lastLine = results[siz - 1]
        if lastLine == winLine:
            return None

    strResult = '\n'.join(results)

    if WHITE in strResult and BLACK in strResult:
        return None

    isGreenIn = GREEN in strResult
    isYellowIn = YELLOW in strResult
    if not isGreenIn and not isYellowIn:
        if WHITE in strResult:
            output.append(WHITEREACT)
        elif BLACK in strResult:
            output.append(BLACKREACT)
        else:
            output.append(GREEN)

    elif isGreenIn and not isYellowIn:
        output.append(GREENREACT)
    elif not isGreenIn and isYellowIn:
        output.append(YELLOWREACT)

    return output


if __name__ == '__main__':
    input = "Wordle 1,000 🎉 X/6\n\n⬜🟩⬜🟨⬜\n⬜🟩⬜🟨⬜\n⬜🟩⬜🟨⬜\n⬜🟩⬜🟨⬜\n⬜🟩⬜🟨⬜\n⬜🟩⬜🟨⬜"

    score = input.split("\n")
    getReactions(score)
