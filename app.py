from flask import Flask, redirect,render_template,url_for,request
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///task.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db=SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(300), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id
        

@app.route( '/', methods=['GET','POST'] )
def home():
    if request.method =='POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return "There was a problem while adding Your Task"
    else:
        tasks = Todo.query.order_by(Todo.date_created)
        return render_template("index.html",tasks=tasks)


@app.route('/delete/<int:id>')
def delete(id):
    task_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "There was a problem while deleting the Task" 


@app.route('/update/<int:id>',methods=['GET','POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return "There was a problem while updating your Task "
    else:
        return render_template('update.html',task=task)            
        


if __name__ == '__main__':
    app.run(debug=True)    