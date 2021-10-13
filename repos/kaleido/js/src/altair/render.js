/**
 * @param {object} spec : vega-lite spec
 * @param {object} embedOptions
 * @param {object} format
**/

// TODO: start here check the savers in altair_saver for what to do
function render (spec,embedOptions,format) {
  let opts = {};

  let errorCode = 0
  let result = null
  let errorMsg = null
  let pdfBgColor = null

  const done = () => {
    if (errorCode !== 0 && !errorMsg) {
      errorMsg = cst.statusMsg[errorCode]
    }

    return {
      code: errorCode,
      message: errorMsg,
      pdfBgColor,
      format,
      result,
      width: info.width,
      height: info.height,
      scale: info.scale,
    }
  }

if (format === 'vega') {
    if (embedOpt.mode === 'vega-lite') {
        vegaLite = (typeof vegaLite === "undefined") ? vl : vegaLite;
        try {
            const compiled = vegaLite.compile(spec);
            spec = compiled.spec;
        } catch(error) {
            done({error: error.toString()})
        }
    }
    done({result: spec});
}