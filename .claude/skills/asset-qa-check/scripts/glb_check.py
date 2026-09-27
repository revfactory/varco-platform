#!/usr/bin/env python3
"""3D 모델(GLB) 검사: 외부 라이브러리 없이 헤더와 JSON 청크를 읽어 구조·면 수·텍스처를 확인한다.

사용법
  glb_check.py games/x/assets/models/mdl_crate.glb --id mdl_crate --acceptance '{"face_max": 20000, "has_texture": true}'
  glb_check.py a.glb b.glb --id mdl_set --expect-count 2 --out _workspace/x/03_assetqa_mdl_set.json

면 수는 삼각형 기준이다. primitive mode 4(TRIANGLES)는 indices 개수/3, 인덱스가 없으면 POSITION 개수/3.
VARCO 에 target_face_type=quad 로 요청해도 GLB 는 삼각형으로 저장되므로 삼각형 수는 요청한 면 수의 약 2배가 된다.
"""
import argparse
import json
import pathlib
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from qa_common import Report, load_acceptance  # noqa: E402

JSON_CHUNK = 0x4E4F534A
BIN_CHUNK = 0x004E4942


def parse_glb(path):
    data = pathlib.Path(path).read_bytes()
    info = {"bytes": len(data)}
    if len(data) < 20:
        raise ValueError("파일이 너무 짧다(GLB 헤더 없음)")
    magic, version, length = struct.unpack_from("<4sII", data, 0)
    info.update(magic=magic.decode("ascii", "replace"), version=version, declared_length=length)
    if magic != b"glTF":
        raise ValueError(f"magic 이 glTF 가 아니다: {magic!r}")
    off, gltf, bin_len = 12, None, 0
    while off + 8 <= len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        body = data[off + 8: off + 8 + clen]
        if ctype == JSON_CHUNK and gltf is None:
            gltf = json.loads(body.decode("utf-8"))
        elif ctype == BIN_CHUNK:
            bin_len = clen
        off += 8 + clen
    if gltf is None:
        raise ValueError("JSON 청크가 없다")
    accessors = gltf.get("accessors", [])
    tris, prims, non_tri = 0, 0, 0
    for mesh in gltf.get("meshes", []):
        for p in mesh.get("primitives", []):
            prims += 1
            mode = p.get("mode", 4)
            if mode != 4:
                non_tri += 1
                continue
            if "indices" in p:
                tris += accessors[p["indices"]]["count"] // 3
            elif "POSITION" in p.get("attributes", {}):
                tris += accessors[p["attributes"]["POSITION"]]["count"] // 3
    mats = gltf.get("materials", [])
    textured = sum(1 for m in mats if (m.get("pbrMetallicRoughness", {}).get("baseColorTexture")
                                        or m.get("normalTexture")))
    info.update(meshes=len(gltf.get("meshes", [])), primitives=prims, non_triangle_primitives=non_tri,
                triangles=tris, materials=len(mats), textured_materials=textured,
                textures=len(gltf.get("textures", [])), images=len(gltf.get("images", [])), bin_chunk_bytes=bin_len,
                generator=(gltf.get("asset") or {}).get("generator"))
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--id", default="model")
    ap.add_argument("--acceptance")
    ap.add_argument("--acceptance-file")
    ap.add_argument("--expect-count", type=int)
    ap.add_argument("--out")
    args = ap.parse_args()
    acc = load_acceptance(args.acceptance, args.acceptance_file)
    rep = Report(args.id)

    existing = [f for f in args.files if pathlib.Path(f).is_file()]
    missing = [f for f in args.files if not pathlib.Path(f).is_file()]
    if args.expect_count is not None or missing:
        exp = args.expect_count if args.expect_count is not None else len(args.files)
        rep.add("file_count", len(existing) == exp, f"{len(existing)}/{exp}", f"GLB 없음: {missing[:5]}",
                "3D 결과를 다시 받는다(varco_client.py result {requestId})")
    if not existing:
        rep.cannot_verify("검사할 GLB 파일이 없다")
        sys.exit(rep.emit(args.out))

    infos, errors = {}, []
    for f in existing:
        try:
            infos[pathlib.Path(f).name] = parse_glb(f)
        except Exception as e:
            errors.append(f"{pathlib.Path(f).name}: {e}")
    rep.add("glb_valid", not errors, f"{len(infos)}/{len(existing)}", f"GLB 형식 오류: {errors}",
            "다시 생성하거나 model_url 에서 다시 내려받는다")
    for name, i in infos.items():
        rep.add(f"{name}:version", i["version"] == 2, f"v{i['version']}", f"{name} glTF 버전 {i['version']}", None)
        rep.add(f"{name}:length", i["declared_length"] == i["bytes"], f"{i['declared_length']}/{i['bytes']}",
                f"{name} 선언 길이와 실제 크기가 다르다(다운로드 중단 의심)", "다시 내려받는다")
        rep.add(f"{name}:has_mesh", i["triangles"] > 0, f"삼각형 {i['triangles']}", f"{name} 메시가 비어 있다",
                "입력 이미지를 바꿔 다시 생성한다")
        if "face_max" in acc:
            rep.add(f"{name}:face_max", i["triangles"] <= acc["face_max"], f"{i['triangles']} ≤ {acc['face_max']}",
                    f"{name} 삼각형 {i['triangles']}개가 상한 {acc['face_max']} 초과",
                    "target_face_num 을 낮춰 다시 생성한다(quad 는 삼각형이 약 2배)")
        if "has_texture" in acc:
            has = i["textured_materials"] > 0 and i["images"] > 0
            rep.add(f"{name}:has_texture", has == bool(acc["has_texture"]),
                    f"텍스처 재질 {i['textured_materials']}, 이미지 {i['images']}",
                    f"{name} 텍스처 기대 {acc['has_texture']}, 실제 {has}",
                    "generate_texture 값을 확인해 다시 생성한다")
    rep.extra["models"] = infos
    sys.exit(rep.emit(args.out))


if __name__ == "__main__":
    main()
