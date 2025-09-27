// 重新应用highlight.js来高亮代码块
if (typeof hljs !== 'undefined') {
    {
        hljs.highlightAll();
    }
}

// 重新渲染 MathJax 公式
if (typeof MathJax !== 'undefined') {
    MathJax.typesetPromise().then(function() {
        console.log("MathJax rendering complete.");
    }).catch(function(error) {
        console.error("MathJax rendering failed:", error);
    });
}