from django.shortcuts import render
import json
import os


# Create your views here.

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
    
    # print(atributesData['root'])

    context = {'htmlTags' : htmlTags, 'htmlAttributes': atributesData, 'categories': categoriesData, 'classes': classes, 'request': req}

    return render(req, "componentBuilder/editmode.html", context)
