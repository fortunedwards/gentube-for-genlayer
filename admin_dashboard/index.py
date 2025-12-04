from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>GenTube Admin Dashboard</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-900 text-white min-h-screen">
        <div class="container mx-auto px-4 py-8">
            <div class="max-w-2xl mx-auto">
                <div class="text-center mb-8">
                    <h1 class="text-4xl font-bold mb-2">GenTube Admin</h1>
                    <p class="text-gray-400">Video Management Dashboard</p>
                </div>
                
                <div class="bg-gray-800 rounded-lg p-6 mb-6">
                    <h2 class="text-xl font-semibold mb-4">🚧 Under Construction</h2>
                    <p class="text-gray-300 mb-4">
                        The admin dashboard is being set up. For now, you can manually manage videos by editing the videos.json file.
                    </p>
                    <div class="space-y-2">
                        <p class="text-sm text-gray-400">• Add videos to the JSON structure</p>
                        <p class="text-sm text-gray-400">• Update the public site automatically</p>
                        <p class="text-sm text-gray-400">• Full admin features coming soon</p>
                    </div>
                </div>
                
                <div class="text-center">
                    <a href="https://gentube-for-genlayer.vercel.app/" 
                       class="inline-block bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded">
                        View Public Site
                    </a>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)