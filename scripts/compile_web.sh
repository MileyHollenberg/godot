#!/bin/sh

scons p=web target=template_release javascript_eval=no
scons p=web target=template_debug javascript_eval=no
