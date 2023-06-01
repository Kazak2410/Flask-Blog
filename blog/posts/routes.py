from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from blog import db
from blog.models import Post, Category, Comment
from blog.posts.forms import PostForm, SearchForm


posts = Blueprint('posts', __name__)


@posts.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        category = Category.query.filter_by(name=form.category.data).first()
        post = Post(title=form.title.data, content=form.content.data, author=current_user, category=category)
        db.session.add(post)
        db.session.commit()
        flash('The post has been created!', 'success')
        return redirect(url_for('posts.home'))
    return render_template('create_post.html', form=form, title='CreatPost')


@posts.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post, title=post.title)


@posts.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('The post has been deleted!', 'success')
    return redirect(url_for('posts.home'))


@posts.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form)


@posts.route('/category/<int:category_id>/')
def category(category_id):
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(category_id=category_id).order_by(Post.date_posted.desc()).paginate(page=page, per_page=3)
    category_name = Category.query.filter_by(id=category_id).first().name
    categories = Category.query.all()
    return render_template('category.html', posts=posts, categories=categories, title=category_name)


@posts.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = Post.query
    if form.validate_on_submit():
        post.searched = form.searched.data
        posts = posts.filter(Post.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Post.title).all()
        return render_template("search.html", form=form, searched=post.searched, posts=posts)


@posts.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


@posts.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=3)
    categories = Category.query.all()
    return render_template('home.html', posts=posts, categories=categories, title='Home')


@posts.route('/create_comment/<post_id>/', methods=['GET', 'POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', 'info')
    else:
        post = Post.query.filter_by(id=post_id).first()
        if post:
            comment = Comment(text=text, author=current_user, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
            flash('Comment has been created!', 'success')
        else:
            flash('Post does not exist.', 'info')

    return redirect(url_for('posts.home'))


@posts.route('/delete_comment/<comment_id>/', methods=['GET', 'POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if current_user.id != comment.author.id and current_user.id != comment.post.author.id:
        flash("You don't have permission", 'danger')
    else:
        db.session.delete(comment)
        db.session.commit()
        flash('Comment has been deleted', 'success')

    return redirect(url_for('posts.home'))
