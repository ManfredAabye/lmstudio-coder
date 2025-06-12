# -*- coding: utf-8 -*-
# API-Kommunikation mit LM Studio

import requests
import time
import logging

class APIClient:
    def __init__(self, base_url="http://localhost:1234/v1"):
        self.base_url = base_url
    
    def ask_lm_studio(self, prompt, language, max_retries=3, retry_delay=5):
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    json={
                        "messages": [
                            {"role": "system", "content": f"Du bist ein {language}-Experte. Antworte NUR mit Code."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 4000
                    },
                    timeout=180
                )
                return response.json()["choices"][0]["message"]["content"]
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                logging.error(f"API-Fehler nach {max_retries} Versuchen: {str(e)}")
                raise
            except Exception as e:
                logging.error(f"Unerwarteter Fehler: {str(e)}")
                raise
