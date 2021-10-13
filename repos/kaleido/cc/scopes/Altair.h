//
// Created by Daylin Morgan on 2021.09.
//
#include "Base.h"
#include "base/bind.h"
#include "base/command_line.h"
#include "base/strings/string_util.h"
#include "base/strings/stringprintf.h"
#include "headless/public/devtools/domains/runtime.h"
#include "../utils.h"
#include <streambuf>
#include <string>
#include <sstream>
#include <iostream>
#include <fstream>


#ifndef CHROMIUM_ALTAIRSCOPE_H
#define CHROMIUM_ALTAIRSCOPE_H

namespace kaleido {
    namespace scopes {

        class AltairScope : public BaseScope {
        public:
            AltairScope();

            ~AltairScope() override;

            AltairScope(const AltairScope &v);

            std::string ScopeName() override;

            std::vector<std::unique_ptr<::headless::runtime::CallArgument>> BuildCallArguments() override;
        };

        AltairScope::AltairScope() {
            // Process plotlyjs
            if (HasCommandLineSwitch("vegajs")) {
                std::string vegajsArg = GetCommandLineSwitch("vegajs");

                // Check if value is a URL
                GURL vegajsUrl(vegajsArg);
                if (vegajsUrl.is_valid()) {
                    scriptTags.push_back(vegajsArg);
                } else {
                    // Check if this is a local file path
                    if (std::ifstream(vegajsArg)) {
                        localScriptFiles.emplace_back(vegajsArg);
                    } else {
                        errorMessage = base::StringPrintf("--vegajs argument is not a valid URL or file path: %s",
                                                          vegajsArg.c_str());
                        return;
                    }
                }
            } else {
                scriptTags.emplace_back("https://cdn.jsdelivr.net/npm/vega@5");
                scriptTags.emplace_back("https://cdn.jsdelivr.net/npm/vega-lite@5");
                scriptTags.emplace_back("https://cdn.jsdelivr.net/npm/vega-embed@6");
        }

        AltairScope::~AltairScope() {}

        AltairScope::AltairScope(const AltairScope &v) {}

        std::string AltairScope::ScopeName() {
            return "altair";
        }

        std::vector<std::unique_ptr<::headless::runtime::CallArgument>> AltairScope::BuildCallArguments() {
            std::vector<std::unique_ptr<::headless::runtime::CallArgument>> args;

            return args;
        }
    }
}

#endif //CHROMIUM_ALTAIRSCOPE_H
