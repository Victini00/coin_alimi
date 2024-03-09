<presetting>
1. api 발급

일단 binance에 들어가서, api key를 발급받는다.
선물 계좌 enable 체크 후, 내 ip만 가능하도록 만들기.

API key와 Secret Key를 받는다.

환경변수에 이를 저장해두면, os.environ.get("변수이름")으로
불러올 수 있다.

2. 모듈 설치
pip install python-binance 를 통해 바이낸스 모듈을 설치한다.
이제 import하여 사용할 수 있다.

모듈 설치 오류가 나면 파이썬 버전을 다른 걸로 선택하자.


# 암호화폐 티커의 정보
ask와 bid: 매도 호가와 매수 호가
close: 현재가
