#import flaskr as framework
import quartr as framework

app = framework.Create_App()
app.run(host='0.0.0.0', port=5200,  debug=True)
