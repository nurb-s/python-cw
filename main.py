from flask import Flask, jsonify, abort, request, make_response
import os.path
from tempfile import NamedTemporaryFile
from PIL import Image
# import numpy as np
# from matplotlib import pyplot as plt

app = Flask(__name__)
tasks = []


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/shervarly/api/v1.0/info/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = next((x for x in tasks if x["id"] == task_id), None)
    if task is None:
        abort(404)
    return jsonify({'size': os.path.getsize(task['file'])}, {'name': task['name']})


@app.route('/shervarly/api/v1.0/image_id/<int:task_id>', methods=['GET'])
def get_image_id(task_id):
    task = next((x for x in tasks if x["id"] == task_id), None)
    if task is None:
        abort(404)
    with open(task['file'], 'rb') as fp:
        image_binary = fp.read()
    response = make_response(image_binary)
    response.headers.set('Content-Type', 'image/%s' % task['image_type'])
    response.headers.set(
        'Content-Disposition', 'attachment', filename='%s' % task['name'] + '.' + task['image_type'])
    return response


@app.route('/shervarly/api/v1.0/image_name/<string:task_name>', methods=['GET'])
def get_image_name(task_name):
    task = next((x for x in tasks if x["name"] == task_name), None)
    if task is None:
        abort(404)
    with open(task['file'], 'rb') as fp:
        image_binary = fp.read()
    response = make_response(image_binary)
    response.headers.set('Content-Type', 'image/%s' % task['image_type'])
    response.headers.set(
        'Content-Disposition', 'attachment', filename='%s' % task['name'] + '.' + task['image_type'])
    return response


@app.route('/shervarly/api/v1.0/stretch', methods=['GET'])
def get_stretch():
    if len(tasks) <= 0:
        abort(404)
    files = []
    for task in tasks:
        files.append(task['file'])

    image_path = 'ydoli.jpeg'
    new_image_path = 'ne_ydoly.jpeg'
    new_width = 900
    new_height = 500

    img = Image.open(image_path)
    # изменяем размер
    new_image = img.resize((new_width, new_height))
    # new_image.show()
    new_image.save(new_image_path)
    with open(new_image_path, 'rb') as fp:
        image_binary = fp.read()
    response = make_response(image_binary)
    response.headers.set('Content-Type', 'image/jpeg')
    response.headers.set(
        'Content-Disposition', 'attachment', filename=new_image_path)
    return response

@app.route('/shervarly/api/v1.0/send', methods=['POST'])
def create_task():
    if request.files.__len__() != 1:
        abort(400)
    for file in request.files:
        if request.files[file].content_type.partition('/')[0] != 'image':
            abort(400)
        if len(tasks) == 0:
            id_file = 1
        else:
            id_file = tasks[-1]['id'] + 1
        request.files[file].stream.fileno()
        temp_file = NamedTemporaryFile(delete=False)
        temp_file.write(request.files[file].stream.read())
        task = {
            'id': id_file,
            'file': temp_file.name,
            'name': file,
            'image_type': request.files[file].content_type.partition('/')[2]
        }
        tasks.append(task)

        return jsonify({'id': id_file}, {'name': file}), 201


@app.route('/shervarly/api/v1.0/delete/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = next((x for x in tasks if x["id"] == task_id), None)
    if task is None:
        abort(404)
    tasks.remove(task)
    return jsonify({'result': True})


if __name__ == '__main__':
    app.run(host='0.0.0.0')
