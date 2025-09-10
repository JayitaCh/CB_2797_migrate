window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: L.control.sideBySide,
        function1: function() {
            L.control.sideBySide(this._layers[0], this._layers[1]).addTo(this._map);
        },
        function2: function(map, context) {
                const left = context.refs.left;
                const right = context.refs.right;
                L.control.sideBySide(left, right).addTo(map);
            }

            ,
        function3: function() {
            const leftlayer = this.refs.left;
            const rightlayer = this.refs.right;
            L.control.sideBySide(leftlayer, rightlayer).addTo(this.map);
        }

    }
});