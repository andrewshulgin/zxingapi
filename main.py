from io import BytesIO

from fastapi import FastAPI, UploadFile, responses

from PIL import Image
import zxingcpp

app = FastAPI()


@app.post("/read")
async def read(
    file: UploadFile,
    response: responses.Response,
    format: str = "",
    formats: str = "",
    try_rotate: bool = True,
    try_downscale: bool = True,
    pure: bool = False,
):
    try:
        barcode_formats = (
            zxingcpp.barcode_formats_from_str(formats)
            if formats
            else zxingcpp.barcode_format_from_str(format)
        )
    except ValueError as e:
        response.status_code = 400
        return {"error": str(e)}

    results = zxingcpp.read_barcodes(
        Image.open(file.file),
        formats=barcode_formats,
        try_rotate=try_rotate,
        try_downscale=try_downscale,
        is_pure=pure,
    )
    return [
        {
            "bytes": result.bytes,
            "content_type": result.content_type.name,
            "format": result.format.name,
            "orientation": result.orientation,
            "position": {
                (result.position.top_left.x, result.position.top_left.y),
                (result.position.top_right.x, result.position.top_right.y),
                (result.position.bottom_right.x, result.position.bottom_right.y),
                (result.position.bottom_left.x, result.position.bottom_left.y),
            },
            "text": result.text,
            "valid": result.valid,
        }
        for result in results
    ]


@app.get(
    "/write/{format}",
    responses={200: {"content": {"image/png": {}}}},
    response_class=responses.Response,
)
async def write(
    format: str,
    text: str,
    response: responses.Response,
    width: int = 0,
    height: int = 0,
    quiet_zone: int = -1,
    ec_level: int = 0,
):
    try:
        barcode_format = zxingcpp.barcode_format_from_str(format)
        if barcode_format is None:
            raise ValueError("Format not specified")
    except ValueError as e:
        response.status_code = 400
        return responses.JSONResponse({"error": str(e)})

    file = BytesIO()
    result = zxingcpp.write_barcode(
        format=barcode_format,
        text=text,
        width=width,
        height=height,
        quiet_zone=quiet_zone,
        ec_level=ec_level,
    )
    Image.fromarray(result).save(file, "PNG")
    file.seek(0)
    return responses.Response(content=file.read(), media_type="image/png")
