const style = document.createElement('style');

style.appendChild(document.createTextNode(`
    .app-talk.in-call .top-bar.in-call,
    .local-media-controls,
    #localVideoContainer,
    button.stripe--collapse {
        display: none;
    }
`));

document.getElementsByTagName('head')[0].appendChild(style);
