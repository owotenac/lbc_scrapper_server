from flask_cors import CORS
from flask import Flask
from reader import searchItems, getItem
from model import ai_analysis
from auto_reader import auto_reader, coldData, removeColdData, saveItem

app = Flask(__name__)


@app.route('/')
def index():
    return "Ready"

app.add_url_rule('/api/searchitems', 'searchitems', searchItems)
app.add_url_rule('/api/getitem', 'getitem', getItem)
app.add_url_rule('/api/autoreader', 'autoreader', auto_reader)
app.add_url_rule('/api/colddata', 'colddata', coldData)
app.add_url_rule('/api/removecolddata', 'removecolddata', removeColdData, methods=['DELETE'])
app.add_url_rule('/api/ai_analysis', 'ai_analysis', ai_analysis, methods=['POST'])
app.add_url_rule('/api/saveitem', 'saveitem', saveItem, methods=['POST'])


CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})

def main():
    app.run(debug=True,port=5002 , use_reloader=False)

if __name__ == "__main__":
    main()