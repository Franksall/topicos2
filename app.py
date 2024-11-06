import os
from flask import Flask, render_template, request, jsonify, send_file
from io import StringIO
import art

app = Flask(__name__)

def find_in_dict(buffer, dictionary):
    shift = len(dictionary)
    substring = ""
    for character in buffer:
        substring_tmp = substring + character
        shift_tmp = dictionary.rfind(substring_tmp)
        if shift_tmp < 0:
            break
        substring = substring_tmp
        shift = shift_tmp
    return len(substring), len(dictionary) - shift

def compress(message, buffer_size, dictionary_size):
    dictionary = ""
    buffer = message[:buffer_size]
    output = []
    while len(buffer) != 0:
        size, shift = find_in_dict(buffer, dictionary)
        dictionary += message[:size + 1]
        dictionary = dictionary[-dictionary_size:]
        message = message[size:]
        last_character = message[:1]
        message = message[1:]
        buffer = message[:buffer_size]
        if shift != 0 or size != 0:
            output.append((shift, size, last_character))
        else:
            output.append(last_character)
    return output

def decompress(compressed_message):
    message = ""
    for part in compressed_message:
        if len(part) != 1:
            shift, size, character = part
            message += message[-shift:][:size] + character
        else:
            message += part
    return message

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress_message():
    message = request.form['message']
    buffer_size = int(request.form['buffer_size'])
    dictionary_size = int(request.form['dictionary_size'])
    compressed = compress(message, buffer_size, dictionary_size)
    return jsonify(compressed)

@app.route('/decompress', methods=['POST'])
def decompress_message():
    compressed = eval(request.form['compressed'])
    decompressed = decompress(compressed)
    return jsonify(decompressed)

@app.route('/download', methods=['POST'])
def download_file():
    compressed_message = request.form['compressed_message']
    buffer = StringIO()
    buffer.write(str(compressed_message))
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, attachment_filename='compressed_message.txt', mimetype='text/plain')


if __name__ == '__main__':
    app.run(debug=True)
