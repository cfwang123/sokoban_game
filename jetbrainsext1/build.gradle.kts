plugins {
    id("java")
    id("org.jetbrains.kotlin.jvm") version "1.9.22"
    // 真机插件工程使用: id("org.jetbrains.intellij") version "..."
}

group = "com.whj.sokoban"
version = "1.0.0"

repositories {
    mavenCentral()
}

dependencies {
    // 完整 IntelliJ 插件需:
    // intellij { version.set("2023.3") }
    // 本教学工程仅 Kotlin 源码 + plugin.xml，可用下面控制台主函数验证逻辑
    // implementation 不强制拉取巨大 IDE SDK，避免无网环境失败
}

kotlin {
    jvmToolchain(17)
}

// 无 IntelliJ SDK 时：可编译/运行控制台宿主（见 SokobanConsole.kt）
sourceSets {
    main {
        java.srcDirs("src/main/kotlin")
        resources.srcDirs("src/main/resources")
    }
}

tasks.register<JavaExec>("runConsole") {
    group = "application"
    description = "Run console host without IntelliJ SDK"
    classpath = sourceSets["main"].runtimeClasspath
    mainClass.set("com.whj.sokoban.SokobanConsoleKt")
}
