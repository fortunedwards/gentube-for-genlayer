from flask import Flask

app = Flask(__name__)

@app.route('/')
@app.route('/admin')
@app.route('/admin/')
def admin_redirect():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>GenTube Admin</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-900 text-white">
        <div class="min-h-screen flex items-center justify-center">
            <div class="max-w-md w-full space-y-8 text-center">
                <div>
                    <h2 class="text-3xl font-bold">GenTube Admin</h2>
                    <p class="mt-2 text-gray-400">Video Management Dashboard</p>
                </div>
                <div class="bg-gray-800 p-6 rounded-lg">
                    <p class="text-blue-400 mb-4">🚀 Admin Dashboard Available</p>
                    <a href="https://gentube-admin.vercel.app" 
                       class="inline-block bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                        Access Admin Dashboard
                    </a>
                    <p class="text-sm text-gray-400 mt-4">
                        Deploy the admin_dashboard folder as a separate Vercel project
                    </p>
                </div>
                <div class="text-center">
                    <a href="/" class="text-blue-400 hover:text-blue-300">← Back to Public Archive</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

def handler(request, context):
    return app