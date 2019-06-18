# Copyright (c) 2019 Hiroki Takemura (kekeho)
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from flask import Flask
app = Flask(__name__)


@app.route('/')
def index():
    return "Hi"


if __name__ == "__main__":
    app.run()
