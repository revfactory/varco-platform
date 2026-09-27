API 호출 시, OPENAPI_KEY를 통해 인증이 이루어집니다.
이 키는 사용자에게 발급되며, 애플리케이션이 API를 호출할 때 요청 헤더에 포함되어 사용자를 식별합니다.

#### 인증 방식

모든 요청 헤더에 아래와 같이 OPENAPI_KEY를 포함해야 합니다.


##### Request Example
```bash
curl --location 'https://openapi.ai.nc.com/mt/chat-content/v1/translate' \
--header 'OPENAPI_KEY: 8sh1XXXXX86H5iN5828Jjjjzyb3AAAAn' \
--header 'Content-Type: application/json' \
--data '{
  "TID": "00000000-0000-0000-0000-00000000000",
  "game_code": "linw",
  "provider": "chat",
  "source_lang": "en",
  "source_text": "help help",
  "target_lang": "ko"
}
```
OPENAPI_KEY가 누락되거나 잘못된 경우, HTTP 401 Unauthorized 응답이 반환됩니다.

```bash
{
    "message": "Unauthorized",
    "request_id": "b6dbdd2b6153057bcd3b5b3ae8cdea66"
}
```

#### 주의사항

OPENAPI_KEY는 비공개 자격 증명 정보이므로 외부에 노출되어서는 안 됩니다.

키가 유출될 경우, 타인이 API를 호출하거나 크레딧을 무단 사용할 수 있습니다.

GitHub, Notion, Slack, 프론트엔드 코드 등에 하드코딩하거나 공유하지 마세요.

분실 또는 유출이 의심되는 경우, 즉시 기존 키를 폐기하고 새로운 키를 발급받으십시오.

일부 서비스에서는 OPENAPI_KEY를 통해 API 서비스 접근 권한(Role) 또는 Rate Limit, Credit 사용 한도가 자동으로 결정될 수 있습니다.

테스트 및 운영 환경에서는 서로 다른 Key를 사용하는 것을 권장합니다.

사용하지 않는 키는 삭제하여 보안을 유지하십시오.

