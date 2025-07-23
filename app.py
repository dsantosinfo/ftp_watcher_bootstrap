from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
# MUDE ISSO: Use uma chave secreta forte e complexa em produção!
app.secret_key = 'sua_chave_secreta_muito_segura_aqui_12345'

# Define o caminho para o banco de dados
DATABASE = os.path.join(app.root_path, 'instance', 'configs.db')

def get_db_connection():
    """Retorna uma conexão com o banco de dados SQLite."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
    return conn

# --- Rotas para Sites ---
@app.route('/')
def list_sites():
    """Rota principal para listar todos os sites (destinos FTP)."""
    conn = get_db_connection()
    sites = conn.execute('SELECT * FROM sites ORDER BY name').fetchall()
    conn.close()
    return render_template('sites/index.html', sites=sites)

@app.route('/sites/add', methods=('GET', 'POST'))
def add_site():
    """Rota para adicionar um novo site."""
    if request.method == 'POST':
        name = request.form['name'].strip()
        ftp_host = request.form['ftp_host'].strip()
        ftp_user = request.form['ftp_user'].strip()
        ftp_password = request.form['ftp_password']
        ftp_port = request.form.get('ftp_port', 21, type=int)

        if not all([name, ftp_host, ftp_user, ftp_password]):
            flash('Todos os campos obrigatórios devem ser preenchidos!', 'danger')
            return render_template('sites/add_edit.html', title="Adicionar Novo Site")

        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO sites (name, ftp_host, ftp_user, ftp_password, ftp_port)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, ftp_host, ftp_user, ftp_password, ftp_port))
            conn.commit()
            flash(f'Site "{name}" adicionado com sucesso!', 'success')
            return redirect(url_for('list_sites'))
        except sqlite3.IntegrityError:
            flash(f'Erro: Já existe um site com o nome "{name}". O nome deve ser único.', 'danger')
        except Exception as e:
            flash(f'Erro ao adicionar site: {e}', 'danger')
        finally:
            conn.close()
    return render_template('sites/add_edit.html', title="Adicionar Novo Site")

@app.route('/sites/edit/<int:site_id>', methods=('GET', 'POST'))
def edit_site(site_id):
    """Rota para editar um site existente."""
    conn = get_db_connection()
    site = conn.execute('SELECT * FROM sites WHERE id = ?', (site_id,)).fetchone()

    if not site:
        flash('Site não encontrado para edição!', 'danger')
        conn.close()
        return redirect(url_for('list_sites'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        ftp_host = request.form['ftp_host'].strip()
        ftp_user = request.form['ftp_user'].strip()
        ftp_password = request.form['ftp_password']
        ftp_port = request.form.get('ftp_port', 21, type=int)

        if not all([name, ftp_host, ftp_user, ftp_password]):
            flash('Todos os campos obrigatórios devem ser preenchidos!', 'danger')
            return render_template('sites/add_edit.html', title="Editar Site", site=site)

        try:
            conn.execute('''
                UPDATE sites SET
                    name = ?, ftp_host = ?, ftp_user = ?, ftp_password = ?, ftp_port = ?
                WHERE id = ?
            ''', (name, ftp_host, ftp_user, ftp_password, ftp_port, site_id))
            conn.commit()
            flash(f'Site "{name}" atualizado com sucesso!', 'success')
            return redirect(url_for('list_sites'))
        except sqlite3.IntegrityError:
            flash(f'Erro: Já existe outro site com o nome "{name}". O nome deve ser único.', 'danger')
        except Exception as e:
            flash(f'Erro ao atualizar site: {e}', 'danger')
        finally:
            conn.close()
    else:
        conn.close()
    return render_template('sites/add_edit.html', title="Editar Site", site=site)

@app.route('/sites/delete/<int:site_id>', methods=('POST',))
def delete_site(site_id):
    """Rota para excluir um site e todas as suas pastas relacionadas."""
    conn = get_db_connection()
    site = conn.execute('SELECT name FROM sites WHERE id = ?', (site_id,)).fetchone()
    if site:
        try:
            conn.execute('DELETE FROM sites WHERE id = ?', (site_id,))
            conn.commit()
            flash(f'Site "{site["name"]}" e todas as suas pastas relacionadas foram excluídos com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao excluir site: {e}', 'danger')
        finally:
            conn.close()
    else:
        flash('Site não encontrado para exclusão!', 'danger')
    return redirect(url_for('list_sites'))

# --- Rotas para Pastas ---
@app.route('/sites/<int:site_id>/folders')
def list_folders(site_id):
    """Rota para listar as pastas associadas a um site específico."""
    conn = get_db_connection()
    site = conn.execute('SELECT * FROM sites WHERE id = ?', (site_id,)).fetchone()
    if not site:
        flash('Site não encontrado!', 'danger')
        conn.close()
        return redirect(url_for('list_sites'))
    
    folders = conn.execute('SELECT * FROM folders WHERE site_id = ? ORDER BY local_path', (site_id,)).fetchall()
    conn.close()
    return render_template('folders/index.html', site=site, folders=folders)

@app.route('/sites/<int:site_id>/folders/add', methods=('GET', 'POST'))
def add_folder(site_id):
    """Rota para adicionar uma nova pasta a um site."""
    conn = get_db_connection()
    site = conn.execute('SELECT * FROM sites WHERE id = ?', (site_id,)).fetchone()
    if not site:
        flash('Site não encontrado!', 'danger')
        conn.close()
        return redirect(url_for('list_sites'))

    if request.method == 'POST':
        local_path = request.form['local_path'].strip()
        remote_path = request.form['remote_path'].strip()

        if not all([local_path, remote_path]):
            flash('Todos os campos obrigatórios devem ser preenchidos!', 'danger')
            return render_template('folders/add_edit.html', title=f"Adicionar Pasta para {site['name']}", site=site)

        try:
            conn.execute('''
                INSERT INTO folders (site_id, local_path, remote_path)
                VALUES (?, ?, ?)
            ''', (site_id, local_path, remote_path))
            conn.commit()
            flash(f'Pasta "{local_path}" adicionada com sucesso para "{site["name"]}"!', 'success')
            return redirect(url_for('list_folders', site_id=site_id))
        except sqlite3.IntegrityError:
            flash(f'Erro: Já existe uma pasta monitorada com o caminho local "{local_path}". Caminhos locais devem ser únicos.', 'danger')
        except Exception as e:
            flash(f'Erro ao adicionar pasta: {e}', 'danger')
        finally:
            conn.close()
    return render_template('folders/add_edit.html', title=f"Adicionar Pasta para {site['name']}", site=site)

@app.route('/sites/<int:site_id>/folders/edit/<int:folder_id>', methods=('GET', 'POST'))
def edit_folder(site_id, folder_id):
    """Rota para editar uma pasta existente associada a um site."""
    conn = get_db_connection()
    site = conn.execute('SELECT * FROM sites WHERE id = ?', (site_id,)).fetchone()
    if not site:
        flash('Site não encontrado!', 'danger')
        conn.close()
        return redirect(url_for('list_sites'))

    folder = conn.execute('SELECT * FROM folders WHERE id = ? AND site_id = ?', (folder_id, site_id)).fetchone()
    if not folder:
        flash('Pasta não encontrada para edição ou não pertence a este site!', 'danger')
        conn.close()
        return redirect(url_for('list_folders', site_id=site_id))

    if request.method == 'POST':
        local_path = request.form['local_path'].strip()
        remote_path = request.form['remote_path'].strip()

        if not all([local_path, remote_path]):
            flash('Todos os campos obrigatórios devem ser preenchidos!', 'danger')
            return render_template('folders/add_edit.html', title=f"Editar Pasta para {site['name']}", site=site, folder=folder)
        
        try:
            conn.execute('''
                UPDATE folders SET
                    local_path = ?, remote_path = ?
                WHERE id = ? AND site_id = ?
            ''', (local_path, remote_path, folder_id, site_id))
            conn.commit()
            flash(f'Pasta "{local_path}" atualizada com sucesso para "{site["name"]}"!', 'success')
            return redirect(url_for('list_folders', site_id=site_id))
        except sqlite3.IntegrityError:
            flash(f'Erro: Já existe outra pasta monitorada com o caminho local "{local_path}". Caminhos locais devem ser únicos.', 'danger')
        except Exception as e:
            flash(f'Erro ao atualizar pasta: {e}', 'danger')
        finally:
            conn.close()
    else:
        conn.close()
    return render_template('folders/add_edit.html', title=f"Editar Pasta para {site['name']}", site=site, folder=folder)

@app.route('/sites/<int:site_id>/folders/delete/<int:folder_id>', methods=('POST',))
def delete_folder(site_id, folder_id):
    """Rota para excluir uma pasta de um site."""
    conn = get_db_connection()
    folder = conn.execute('SELECT local_path FROM folders WHERE id = ? AND site_id = ?', (folder_id, site_id)).fetchone()
    if folder:
        try:
            conn.execute('DELETE FROM folders WHERE id = ? AND site_id = ?', (folder_id, site_id))
            conn.commit()
            flash(f'Pasta "{folder["local_path"]}" excluída com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao excluir pasta: {e}', 'danger')
        finally:
            conn.close()
    else:
        flash('Pasta não encontrada para exclusão ou não pertence a este site!', 'danger')
    return redirect(url_for('list_folders', site_id=site_id))

if __name__ == '__main__':
    from config_db import init_db
    init_db() # Garante que o DB e as tabelas existam
    app.run(debug=True) # debug=True para desenvolvimento