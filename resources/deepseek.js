// 重新应用highlight.js来高亮代码块
if (typeof hljs !== 'undefined') {
    {
        hljs.highlightAll();
    }
}

// 重新渲染 MathJax 公式
if (typeof MathJax !== 'undefined') {
    // 检查MathJax版本并使用相应的API
    if (MathJax.version && MathJax.version.startsWith('3')) {
        // MathJax v3
        MathJax.typesetPromise().then(function () {
            console.log("MathJax rendering complete.");
        }).catch(function (error) {
            console.error("MathJax rendering failed:", error);
        });
    } else if (MathJax.typeset) {
        // MathJax v4
        MathJax.typeset();
        console.log("MathJax rendering complete.");
    } else {
        console.log("MathJax is loaded but no suitable API found.");
    }
}