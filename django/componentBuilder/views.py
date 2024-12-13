from django.shortcuts import render
import json
import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Component

@csrf_exempt
def saveComponent(req):
    if req.method == "POST":
        data = json.loads(req.body)
        # print(data["html"])
        # print(data["name"])
        newComponent = Component( 
            html = data["html"] ,
            name = data["name"] 
        )
        newComponent.save()
        return JsonResponse({"created" : {"html": newComponent.html, "name": newComponent.name} })
    return JsonResponse({"test": "minimeow"})

def getComponent(req, component_id):
    component = Component.objects.get(id=component_id)
    toSend = { 
        "id"  : component.id,
        "html": component.html ,
        "name": component.name 
    }
    return JsonResponse({"component" : toSend })

@csrf_exempt
def editMode(req):
    htmlTags = [
        "a", "abbr", "address", "area", "article", "aside", "audio", "b", "base",
        "bdi", "bdo", "blockquote", "body", "br", "button", "canvas", "caption", 
        "cite", "code", "col", "colgroup", "data", "datalist", "dd", "del", "details", 
        "dfn", "dialog", "div", "dl", "dt", "em", "embed", "fieldset", "figcaption", 
        "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "head", "header", 
        "hgroup", "hr", "html", "i", "iframe", "img", "input", "ins", "kbd", "label", 
        "legend", "li", "link", "main", "map", "mark", "meta", "meter", "nav", "noscript", 
        "object", "ol", "optgroup", "option", "output", "p", "picture", "pre", "progress", 
        "q", "rp", "rt", "ruby", "s", "samp", "script", "section", "select", "slot", 
        "small", "source", "span", "strong", "style", "sub", "summary", "sup", "svg", 
        "table", "tbody", "td", "template", "textarea", "tfoot", "th", "thead", "time", 
        "title", "tr", "u", "ul", "var", "video", "wbr"
    ]

    current_dir = os.path.dirname(os.path.abspath(__file__))

    json_file_path = os.path.join(current_dir, "Data/htmlAtributesData.json")
    atributesData = {}
    with open(json_file_path) as f:
        atributesData = json.load(f)

    json_file_path = os.path.join(current_dir, "Data/bootstrapCategories.json")
    categoriesData = {}
    with open(json_file_path) as f:
        categoriesData = json.load(f)
    

    json_file_path = os.path.join(current_dir, "Data/bootstrapClassCategories.json")
    classes = {}
    with open(json_file_path) as f:
        classes = json.load(f)


    dirs = []
    images_info = []
    for dirpath, dirnames, filenames in os.walk("../django/static/img/gallery"):
        dirs += (dirnames)

    for minidir in dirs:
        section = {}
        section["category"] = minidir
        for dirpath, dirnames, filenames in os.walk("../django/static/img/gallery/"+minidir):
            files = []
            for file in filenames:

                file_extension = file.split('.')[-1] if '.' in filenames else ''           
                image_data = {
                    'img_name': file,
                    'img_path': ('/img/gallery/' + minidir +  "/" + file),
                    'img_type': file_extension
                }

                files.append(image_data)
        section["images"] = files

        images_info.append(section)

    print(images_info)

    context = {'htmlTags' : htmlTags, 'htmlAttributes': atributesData, 'categories': categoriesData, 'classes': classes, 'request': req, "gallery": images_info, "components": Component.objects.all()}

    return render(req, "componentBuilder/editmode.html", context)

