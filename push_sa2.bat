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
rem --- Tunisia para: commit + push the country switcher / header fix ---
pushd "%USERPROFILE%\Downloads\para_push\kolasaar-para"
git add -A >> "%~dp0push_sa2.log" 2>&1
git commit -m "Header: country shown once, SA/TN switcher" >> "%~dp0push_sa2.log" 2>&1
git push origin main >> "%~dp0push_sa2.log" 2>&1
echo TN push exit=%errorlevel% >> "%~dp0push_sa2.log"
popd
rem --- Saudi main site: Beauty & Care tile/nav moved up ---
pushd "%USERPROFILE%\Documents\saudi-price-compare"
git add -A >> "%~dp0push_sa2.log" 2>&1
git commit -m "Beauty & Care tile and nav link moved up" >> "%~dp0push_sa2.log" 2>&1
git push origin main >> "%~dp0push_sa2.log" 2>&1
echo MAIN push exit=%errorlevel% >> "%~dp0push_sa2.log"
popd
