<p align="center">
    <img src="https://user-images.githubusercontent.com/16767890/130764254-cb2d7a62-a19d-4c10-92a0-9b897910a7fc.png" width="15%" alt="Metarix BOT"/>
</p>
<h1 align="center">METARIX</h1>
<p align="center">
   <b>Project MBOT v2</b>
</p>
2020년 계획된 MBOT 프로젝트를 재구성한 프로젝트입니다.

## 단계별 개발 현황

MBOT의 기능이 생각보다 다양하게 구성된 관게로 아래에 작업 현황이 기재되어 있습니다.

### Project MBOT
* [ ] Logging Service (3단계)
    * [ ] Backup Chatting Service(BCS) (2단계)
* [ ] Leveling Service(2단계)
* [ ] Management Service(1단계)
    * [x] ~~Black User / Block Bot~~ (취소)<br/>
      본 기능은 악질적인 유저 혹은 악질적인 봇을 차단하고자 지원하는 기능이며, 서버에 해를 자주 가한 유저 혹은 디스코드 봇이 방에 들어온다면 차단을 요청하는 기능입니다.
      > 해당 기능은 사용자의 자율성을 침범한다고 판단하여, 취소하기로 하였습니다.
    * [ ] **~~CPC~~, CPG~~(Copy Paste Channel)~~, (Copy Paste Guild)** (3단계)<br/>
      채널과 서버를 보다 쉽게 복사할 수 있습니다. (백업기능)
    * [ ] Auto Grant Role ▶ Authorize (1단계)<br/>
      자동적으로 역할을 부여하는 기능으로, “유저가 가입했을 때” 혹은 “특정 반응”을 눌렀을 때 부여하는 기능입니다.
      + 추가로 "인증" 기능을 도입하여 사전에 매크로를 차단합니다.
    * [ ] Command Management Service (1단계)
    
### Project MBOT (v2)
* [x] Welcome Message (1단계)
* [x] Ticket (1단계)
* [ ] Custom Service (1단계)

## Notes
아래 사항은 개발에 필요한 노트 자료입니다.

### 티켓 백업데이터 처리방안
```json
{
    "GUILD-ID": [
        {
            "type": "{ setting / (ticket) }",
            "channel": "CHANNEL-ID",
            "author": "Contact AUTHOR-ID"
        }
    ]
}
```
* `channel` 키의 DM 기능(모드 1번)을 사용 할 경우 관리자 문의 채널 ↔ DM 중, 관리자채널 ID 값이 포함됩니다.
* `type` 값이 setting 일 경우, `Ticket` 모델과 동일한 양식이 포함됩니다. (Guild ID 제외)