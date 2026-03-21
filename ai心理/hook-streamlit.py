from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 收集Streamlit的所有数据文件和子模块，解决打包后找不到资源的问题
datas = collect_data_files('streamlit')
hiddenimports = collect_submodules('streamlit')