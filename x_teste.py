import requests

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'pt-BR,pt;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'https://mapas.inmet.gov.br',
    'Referer': 'https://mapas.inmet.gov.br/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 OPR/126.0.0.0',
    'sec-ch-ua': '"Chromium";v="142", "Opera Air";v="126", "Not_A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

json_data = {
    'data_inicio': '2026-01-22',
    'data_fim': '2026-01-22',
    'estacao': 'A934',
    'seed': '14c988c0f336d9b9ce12c49249643b4f2a1beae8&YTJhZjJmNWI4ZGNkNzRiYWJmZDFhMzBhNjNhMGFlNzY4ODUwMjMyMgMTRjOTg4YzBmMzM2ZDliOWNlMTJjNDkyNDk2NDNiNGYyYTFiZWFlOA==',
    'gcap': '0cAFcWeA5Uj1hQUFjzbLg5fHTu86Zf5pbwbA_kc6knUFsXClKi11Wt9W-i2DemDEytSypAhAyWO_33vQqcty1fUdcDuFmjnwgQeTS4ZN0abMdhOWlS5CfYOEGdSN-gKBtP7_lSljV1QUI7_EHdkFzE1b1Olst6IaOCe5A7XHeD5Uxz-5yOexqeiNaFGQKM8lOeDLnyE9TfyXB_iOcJW_nrT1yHt8TEph4gT48LjVqQX6FCilP0MUFN0qJuEniWuC6DXYaib92Ud3u1Bb2dkzw9IgzQvmukUuvaqIjX4OV3S5Qq6FOOOg-MqnkhzHaaw4rFJEN-X7fm-GwaOnR9o4hfEGuEzdyu_BbPrZ9rwieuXP-hit3kXxktTHEQX9cAOeMPCGjo-yvz_Ta6lmK53J4e5rzs1v7vBtE1a2znCafn2NGijFlQxMQ2_DmepHWkeOBikncW5VTh0Cs2WsH5x-OXC8oKqDjaAg757O6JcL34fQSNYpFnQo6LrirEFzoJ0qg-YerR6MT_YDtrtmSqKHbR8dIkE_bUwqurUcJUkjVr3KkDS1-bUJ3MlXn9jxBLmWSZrd2JDqTFsLDy_HmYjpiCqMucZvMC79KbV9nFSpgqA247xkRQvr8qxLCI9eujySYn6qwwNoz4t4ze7A5EbozrFcrlRb8IxWUAvNz_tKhXG--oyC-Ubnqh2Jj8YQVa7xu8Do6KQKPh4woPXWl7LiMzp4cZAGzRgs0Lofl8a7M8PQxV2pRH0iLp5ksEQrYT_-9DZzXJyTC0aMlsR6hRMRNnTe0flksbEseE82PTsBGlw5qoLK3NZ0wITmWAdxWE4ppnjsTsZl-5RNlSgF3aLdeliHtfb5wJbdWmS1fh4dOiFRmaoSiVU1gycaCwwKEx6S6jfFFK8rxxIrIWpZzIYytpUgbMqsQXkCdW-ds9Rg-D-H1Bl5lmcyFjyr2Dh-o_Q8NIR_5I0ORDT15ktapn4mVCQFPiHxOxiwQj0ss0CDAKAYKT3VQpjXkBd6hmyJOB7pL-7a0qh8CttNb0CXoyQtgn_NQ9EZ9rbp1UD1wyYTIlN5MfTR-bL-7xoYc_ZU2gg65p68aplFgf21xGsCnBMu76L2Y4wRYfVtRd7YX5FGmFluEl2Vd37TJfucP1S21LWqs3VwFj18tUGwoQZYrtdq3cfXJ7D2pXuh9lri0bbBggKcCQagP9cs6cYgytPBkXZcTy1kK2ogSS9OU4YA_-MYP-nm3mq2SOli2unT8zAlnHda3aXGyovwwnDhGdhDTyEmvXGIQptVlLTa3SE8Eo4hqKk6ndPyW64OX5m_j5mdz_ka8gwqKsuvzigV9MrQH7jQR5zLg2rlI2TfofbsMCrBs4TNH_flganZA0JhQ9X849ZuMoX7sJ0o3pN_MDfK84b-L9N0UFjtOmF9vhkgX8mYqavxOHy39U-v_IdkhisuThA8uo3mkz3ZmIjoBkxUNkY6BGenArXL5u7qJgaWs3woQFO_IMGceiPsxkH973h1NAzTfG9wBm1VV-zqRa83KJA7wHHM4QTcdRX3uL6ulmptQwMN7rWIaKwjuJeGWj7ArWW1-hLtX0dadTCLXz_HtpQni9_eztB48Eyp-GW0i8VYclrVw3DusgP48qMDouTq5Ir_LIfxxM8m1og31OUQjExj8vGa_LBYG4BAcLBZ3E1PkfAA4GLxIbEB27Zg',
}

response = requests.post('https://apitempo.inmet.gov.br/estacao/front', headers=headers, json=json_data)

# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
#data = '{"data_inicio":"2026-01-22","data_fim":"2026-01-22","estacao":"A934","seed":"14c988c0f336d9b9ce12c49249643b4f2a1beae8&YTJhZjJmNWI4ZGNkNzRiYWJmZDFhMzBhNjNhMGFlNzY4ODUwMjMyMgMTRjOTg4YzBmMzM2ZDliOWNlMTJjNDkyNDk2NDNiNGYyYTFiZWFlOA==","gcap":"0cAFcWeA5Uj1hQUFjzbLg5fHTu86Zf5pbwbA_kc6knUFsXClKi11Wt9W-i2DemDEytSypAhAyWO_33vQqcty1fUdcDuFmjnwgQeTS4ZN0abMdhOWlS5CfYOEGdSN-gKBtP7_lSljV1QUI7_EHdkFzE1b1Olst6IaOCe5A7XHeD5Uxz-5yOexqeiNaFGQKM8lOeDLnyE9TfyXB_iOcJW_nrT1yHt8TEph4gT48LjVqQX6FCilP0MUFN0qJuEniWuC6DXYaib92Ud3u1Bb2dkzw9IgzQvmukUuvaqIjX4OV3S5Qq6FOOOg-MqnkhzHaaw4rFJEN-X7fm-GwaOnR9o4hfEGuEzdyu_BbPrZ9rwieuXP-hit3kXxktTHEQX9cAOeMPCGjo-yvz_Ta6lmK53J4e5rzs1v7vBtE1a2znCafn2NGijFlQxMQ2_DmepHWkeOBikncW5VTh0Cs2WsH5x-OXC8oKqDjaAg757O6JcL34fQSNYpFnQo6LrirEFzoJ0qg-YerR6MT_YDtrtmSqKHbR8dIkE_bUwqurUcJUkjVr3KkDS1-bUJ3MlXn9jxBLmWSZrd2JDqTFsLDy_HmYjpiCqMucZvMC79KbV9nFSpgqA247xkRQvr8qxLCI9eujySYn6qwwNoz4t4ze7A5EbozrFcrlRb8IxWUAvNz_tKhXG--oyC-Ubnqh2Jj8YQVa7xu8Do6KQKPh4woPXWl7LiMzp4cZAGzRgs0Lofl8a7M8PQxV2pRH0iLp5ksEQrYT_-9DZzXJyTC0aMlsR6hRMRNnTe0flksbEseE82PTsBGlw5qoLK3NZ0wITmWAdxWE4ppnjsTsZl-5RNlSgF3aLdeliHtfb5wJbdWmS1fh4dOiFRmaoSiVU1gycaCwwKEx6S6jfFFK8rxxIrIWpZzIYytpUgbMqsQXkCdW-ds9Rg-D-H1Bl5lmcyFjyr2Dh-o_Q8NIR_5I0ORDT15ktapn4mVCQFPiHxOxiwQj0ss0CDAKAYKT3VQpjXkBd6hmyJOB7pL-7a0qh8CttNb0CXoyQtgn_NQ9EZ9rbp1UD1wyYTIlN5MfTR-bL-7xoYc_ZU2gg65p68aplFgf21xGsCnBMu76L2Y4wRYfVtRd7YX5FGmFluEl2Vd37TJfucP1S21LWqs3VwFj18tUGwoQZYrtdq3cfXJ7D2pXuh9lri0bbBggKcCQagP9cs6cYgytPBkXZcTy1kK2ogSS9OU4YA_-MYP-nm3mq2SOli2unT8zAlnHda3aXGyovwwnDhGdhDTyEmvXGIQptVlLTa3SE8Eo4hqKk6ndPyW64OX5m_j5mdz_ka8gwqKsuvzigV9MrQH7jQR5zLg2rlI2TfofbsMCrBs4TNH_flganZA0JhQ9X849ZuMoX7sJ0o3pN_MDfK84b-L9N0UFjtOmF9vhkgX8mYqavxOHy39U-v_IdkhisuThA8uo3mkz3ZmIjoBkxUNkY6BGenArXL5u7qJgaWs3woQFO_IMGceiPsxkH973h1NAzTfG9wBm1VV-zqRa83KJA7wHHM4QTcdRX3uL6ulmptQwMN7rWIaKwjuJeGWj7ArWW1-hLtX0dadTCLXz_HtpQni9_eztB48Eyp-GW0i8VYclrVw3DusgP48qMDouTq5Ir_LIfxxM8m1og31OUQjExj8vGa_LBYG4BAcLBZ3E1PkfAA4GLxIbEB27Zg"}'
#response = requests.post('https://apitempo.inmet.gov.br/estacao/front', headers=headers, data=data)