## VARCO 3D API
VARCO 3D 서비스의 기능을 API로 사용할 수 있습니다.\
이미지/텍스트 입력으로 3D 애셋을 생성하여, 모델링 작업 없이 아이디어를 즉시 3D로 구현할 수 있습니다.

[VARCO 3D 서비스 바로가기](https://3d.varco.ai/explore)

![2D to 3D Concept](https://3d.varco.ai/api/objects/ae3f8b361d1b952ba761ad45cfd48f82.png)

## 제공 서비스

### Image to 3D
입력 이미지를 기반으로 3D 메시와 텍스처를 생성합니다.
- Highpoly 메시 생성 → 리메시(Remesh) → UV Unwrap → 텍스처 생성의 순서로 처리됩니다.
- 텍스처 생성은 옵션을 통해 비활성화 가능하며, Diffuse Map과 Normal Map을 제공합니다.
- 원하는 Face 타입(Tri/Quad)과 Face 개수(1,000~300,000)를 설정하여 생성할 수 있습니다.

### Text to 3D
(Coming Soon)
<br/>

## 활용 시나리오
<table>
  <tr>
    <td style="width: 400px;">
      <a href="https://www.youtube.com/watch?v=-ymZNiBBmeM">
        <img src="https://3d.varco.ai/api/objects/ced946eb9cb1f5ab5b0d903e40147296.jpg">
      </a>
    </td>
    <td>
      <h3>Cinematic Artwork</h3>
      Image to 3D 기능을 활용해 파츠 단위 모델을 생성하고<br>
      조립하여 시네마틱 아트워크를 제작한 사례입니다.<br>
      <a href="https://www.youtube.com/shorts/yO2XeokkToY">작업 워크플로우 확인하기</a>
    </td>
  </tr>
   <tr>
    <td style="width: 400px;">
      <a href="https://youtu.be/gmyk7O-b5xg?si=Mv5Xa6t53W6mkAcb">
        <img src="https://3d.varco.ai/api/objects/5e76b0af39b047dc410fb748a7636c9c.jpg">
      </a>
    </td>
    <td>
      <h3>Scene / Game Prototyping</h3>
      기획 단계에서 3D 에셋을 빠르게 생성하여<br>
      씬 구성 및 플레이 테스트에 활용한 사례입니다.<br>
      <a href="https://youtu.be/gmyk7O-b5xg?si=LqenR_3U4LzO6IlQ">튜토리얼 확인하기</a>
    </td>
  </tr>
  <tr>
    <td style="width: 400px;">
      <img src="https://3d.varco.ai/api/objects/269493ca72996964a7fa233166864495.png">
    </td>
    <td>
      <h3>In-Game 3D Prop 제작</h3>
      게임 이벤트용 배경 및 서브 프랍을 Image to 3D로 생성하고<br>
      아이디어 리뷰 및 가모델링으로 활용한 사례입니다.<br>
    </td>
  </tr>
</table>


<!-- ## API 서비스 별 가격 표

API 서비스별로 최적화된 과금 단위를 제공합니다. 사용자는 필요한 기능만 선택해 사용할 수 있으며, 각 API의 사용량에 따라 명확하고 일관된 요금이 산정됩니다. 모든 요금은 1회 호출 단가 기준으로 계산되며, 사용량은 대시보드에서 확인할 수 있습니다.

| 서비스 | 과금 단위 | 기본 단가 |
| :--- | :--- | :--- |
| Image to 3D (텍스처 포함) | 호출당 | 200 크레딧 |
| Image to 3D (메시만) | 호출당 | 100 크레딧 | -->
