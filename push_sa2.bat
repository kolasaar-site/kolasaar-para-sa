@echo off
cd /d "%~dp0"
echo Publishing... > push_sa2.log
if not exist ".git" (
  git init -b main >> push_sa2.log 2>&1
  git remote add origin https://github.com/kolasaar-site/kolasaar-para-sa.git >> push_sa2.log 2>&1
)
git config user.name kolasaar-site >> push_sa2.log 2>&1
git config user.email kolasaar-site@users.noreply.github.com >> push_sa2.log 2>&1
git add -A >> push_sa2.log 2>&1
git commit -m "Update SA data" >> push_sa2.log 2>&1
git push -u origin main >> push_sa2.log 2>&1
echo push exit=%errorlevel% >> push_sa2.log
echo DONE >> push_sa2.log
