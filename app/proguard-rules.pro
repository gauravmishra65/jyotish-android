# R8 rules for the release build. Chaquopy ships its own consumer rules for com.chaquo.python.
# The app's Kotlin code is called from Kotlin only (Python is called through Python.getModule), so nothing of ours
# needs keeping by name. Keep line numbers so crash reports from testers can be read with the mapping file.
-keepattributes SourceFile,LineNumberTable
-renamesourcefileattribute SourceFile
