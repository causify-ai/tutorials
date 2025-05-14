{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "28c4a5c6-38aa-4c67-b2cc-f08b3ebbc96b",
   "metadata": {},
   "outputs": [],
   "source": [
    "import requests\n",
    "\n",
    "def fetch_campaigns(api_url, api_key):\n",
    "    headers = {\n",
    "        \"Api-Token\": api_key\n",
    "    }\n",
    "    response = requests.get(api_url, headers=headers)\n",
    "    return response.json()\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "877a27b3-4c48-44e2-be3a-2472b0e39645",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
