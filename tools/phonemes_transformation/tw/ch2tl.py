# !/usr/bin/env python
# _*_coding:utf-8_*_

import socket
import struct
import argparse
import json

def askForService(text:str):
    '''
        將輸入的中文經過名詞片語解析、文法矯正和翻譯轉換成台羅拼音。\
        若輸入為台羅，則輸出亦為台羅，可將符號調台羅轉成數字調台羅。\
        若輸入為中文，輸出為一個json格式，包含每個詞對應到的台羅，和整句話的台羅拼音。\
        例如: input = 肚子感覺疼-> output = {'肚子': 'pak-tóo', '感覺': 'kám-kak', '疼': 'thiànn', 'tailuo': 'pak4-too2 kam2-kak4 thiann3'}
        Params:
            text:       (str) Text will be translate from Chinese to Tai-Luo.
    '''
    global HOST
    global PORT
    global TOKEN
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        if len(text)==0:
            raise  ValueError ("Input text should not be empty!!!")
        sock.connect((HOST, PORT))
        msg = bytes(TOKEN + "@@@" + text, "utf-8")
        msg = struct.pack(">I", len(msg)) + msg
        sock.sendall(msg)
        result=""
        while True:
            l = sock.recv(8192)
            if not l:
                break
            result += l.decode(encoding="UTF-8")
            TLresult = json.loads(result)
    except Exception as e:
        print(e)
        return {"tailuo": "Exceptions occurs"}
    finally:
        sock.close()

    return TLresult

global HOST
global PORT
global TOKEN
HOST, PORT = "140.116.245.157", 2002
TOKEN = "mi2stts"

if __name__=='__main__':
    text = "路透社報導，現任俄羅斯國家安全會議（Russian Security Council）副主席的麥維德夫說，在「令人厭惡、幾乎可說是法西斯主義的基輔政權」被推翻、烏克蘭完全非軍事化前，莫斯科將繼續在烏國發動戰爭。普亭在25日曝光的訪問中說，俄羅斯已準備好要與參戰各方進行談判，但基輔和其西方支持者拒絕參與談判。麥維德夫是俄烏戰爭最鷹派的支持者之一，經常譴責西方，指控西方企圖分裂俄羅斯，以使烏克蘭受益。麥維德夫於2008年至2012年擔任總統期間，曾自詡為自由的現代主義者。麥維德夫在為俄國官方報紙《俄羅斯日報》（Rossiyskaya Gazeta）撰寫的一篇4500字文章中問道：「西方是否準備好在基輔手下對我們發動全面戰爭，包括核戰？」「如今唯一能阻止我們敵人的辦法，是讓他們了解俄羅斯將以國家核震懾政策的基本原則為指導。倘若出現真正的威脅，俄國將採取行動。」普亭和其他俄羅斯高官一再表示，根據俄羅斯的核武政策，領土完整若受到威脅，便可動用核武。專家表示，俄羅斯坐擁全球最大的核武庫，擁有近6000枚核彈頭。本月稍早，普亭表示核戰風險正在升高，但他強調俄羅斯「沒瘋」，主張俄國的核武庫純粹是防禦性質。麥維德夫說：「西方國家一方面渴望盡可能地羞辱、冒犯、分裂和摧毀俄羅斯，一方面又希望避免核災難。」他說，如果俄羅斯得不到它所要求的安全保障，「這個世界將持續在第3次世界大戰和核災難的邊緣搖搖欲墜。 Zelenskiy）發表耶誕談話說，儘管數以百萬計人因俄羅斯攻擊而陷入黑暗，烏克蘭人不會屈服，將會創造自己的奇蹟。俄軍平安夜當天對烏南赫爾松市（Kherson）砲擊，造成至少10死58傷。澤倫斯基耶誕談話堅抗俄：我們會創造自己的奇蹟。澤倫斯基24日在影片中表示，自由要付出高昂代價，但奴役代價更高。他說：「我們在戰爭開始時忍下來了，抵擋了攻擊、威脅、核子威脅、恐怖、飛彈攻擊，這個冬天我們也會熬過去，因為我們知道我們為何而戰。」澤倫斯基在影片中說，「即使漆黑一片，我們也會找到彼此緊緊擁抱。如果沒有暖氣，我們會長時間擁抱彼此，互相取暖」、「我們會一如既往地微笑，但有一點不同：我們不會等待奇蹟出現，因為我們自己正在創造奇蹟。」俄軍平安夜砲擊赫爾松巿，澤倫斯基：繼續對抗邪惡。儘管俄軍早已撤離赫爾松市，但當地仍在莫斯科武器射程內，受到的威脅也未解除。澤倫斯基24日發布照片說：「這是赫爾松在聖誕節前一日早晨，市中心的狀況。」照片內容顯示，街上遍布著火的車輛、粉碎的窗戶玻璃和屍體。俄軍於平安夜當天對赫爾松市發動砲擊，造成至少10人死亡、58人受傷。澤倫斯基指控俄軍「為恐嚇和享樂而殺戮人命」。挺俄侵烏遭西方制裁，白羅斯估經濟萎縮4％。白羅斯總理高羅夫欽科（Roman Golovchenko）說，白羅斯經濟今年料將因為西方國家祭出懲罰性措施而萎縮4％，這個數字遠低於若干預測。他告訴國營電視台：「你知道的，先前外界對我們所作的預測，從（經濟）徹底崩盤到掉了2成都有。」逃海外俄羅斯人，國會議長：將遭立法加稅。俄羅斯國會「國家院」（State Duma，下議院）議長沃洛金（Vyacheslav Volodin）表示，國家院正準備立法對離開國境的公民加稅。俄羅斯2月揮軍烏克蘭後，已有許多人前往海外。沃洛金在加密通訊軟體Telegram發文指出：「對離開俄羅斯聯邦的人取消優惠，並且對他們提高稅率，相關作法是正確的……我們正致力進行適當修法。」"
    text = "我想回家"
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', default=text, help='Text will be translate from Chinese to Tai-Luo.')
    args = parser.parse_args()
    result = askForService(text=args.text)
    print(result)
    print(result['tailuo']) #不含轉調
