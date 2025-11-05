import json
import hashlib
import codecs
import os
import glob

def calculate_hash(file_path):
    """计算文件的 SHA1 哈希值"""
    with open(file_path, "rb") as f:
        bs = f.read()
        return hashlib.sha1(bs).hexdigest().upper()

def get_repo_url(repo_owner, repo_name, branch):
    """生成 GitHub raw 内容 URL"""
    return f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{branch}"

def update_assets():
    """更新 asset.json 文件"""
    # 读取现有的 asset.json
    with codecs.open("asset.json", "r", encoding="utf-8") as f:
        asset_json = json.load(f)
    
    # 获取当前仓库信息
    with open(".git/config", "r", encoding="utf-8") as f:
        git_config = f.read()
        # 从 git config 中提取仓库信息
        for line in git_config.split("\n"):
            if "url = " in line and "github.com" in line:
                # 格式可能是 https://github.com/owner/repo.git 或 git@github.com:owner/repo.git
                if "https://" in line:
                    repo_url = line.split("github.com/")[1].strip()
                else:
                    repo_url = line.split("github.com:")[1].strip()
                repo_url = repo_url.replace(".git", "")
                repo_owner, repo_name = repo_url.split("/")
                break
    
    # 获取当前分支
    with open(".git/HEAD", "r") as f:
        ref = f.read().strip()
        branch = ref.split("/")[-1] if "/" in ref else "main"
    
    base_url = get_repo_url(repo_owner, repo_name, branch)
    
    # 扫描 UIRes 目录下的所有文件
    new_assets = []
    for file_path in glob.glob("UIRes/**/*", recursive=True):
        if os.path.isfile(file_path):
            # 计算文件哈希
            file_hash = calculate_hash(file_path)
            
            # 处理文件路径，统一使用正斜杠
            file_path = file_path.replace("\\", "/")
            
            # 特殊处理 NotoSansCJKsc-Medium.otf 字体
            if file_path.endswith("NotoSansCJKsc-Medium.otf"):
                url = "https://mirrors.ustc.edu.cn/CTAN/fonts/notocjksc/NotoSansCJKsc-Medium.otf"
            else:
                url = f"{base_url}/{file_path}"
            
            # 创建资源项
            asset_item = {
                "Url": url,
                "FileName": file_path,
                "Hash": file_hash
            }
            new_assets.append(asset_item)
    
    # 更新资源列表
    asset_json["Assets"] = new_assets
    
    # 保存更新后的 asset.json
    with codecs.open("assetCN.json", "w", encoding="utf-8") as f:
        json.dump(asset_json, f, indent=4, ensure_ascii=False)
    
    print(f"Updated assetCN.json - Version: {asset_json['Version']}")
    print(f"Total assets: {len(new_assets)}")

if __name__ == "__main__":
    update_assets()
