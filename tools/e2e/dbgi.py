exec(open('instant.py').read().split("    pg.locator('.sp-v__sheet-item summary').first.click()")[0].replace("b.close()",""))
print(pg.evaluate("[document.activeElement?.outerHTML.slice(0,120), document.querySelector('#talk').open, document.querySelectorAll('.sp-v__sheet-item').length]"))
