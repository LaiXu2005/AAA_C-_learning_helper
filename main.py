from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from enum import Enum
from html import escape
from importlib import import_module
from pathlib import Path
from textwrap import dedent
from typing import Any, Callable


QT_WIDGETS = (
    "QApplication QFrame QHBoxLayout QLabel QMainWindow QMessageBox "
    "QPushButton QScrollArea QStackedWidget QTextBrowser QTreeWidget "
    "QTreeWidgetItem QVBoxLayout QWidget"
).split()

qt_import_error: Exception | None = None
for binding in ("PySide6", "PyQt6", "PyQt5"):
    try:
        core = import_module(f"{binding}.QtCore")
        widgets = import_module(f"{binding}.QtWidgets")
        Qt = core.Qt
        globals().update({name: getattr(widgets, name) for name in QT_WIDGETS})
        qt_import_error = None
        break
    except ImportError as exc:
        qt_import_error = exc

if qt_import_error is not None:
    raise SystemExit(
        "未检测到 Qt 绑定。请安装 PySide6、PyQt6 或 PyQt5。"
    )


# 获取不同 Qt 版本中名称可能不同的枚举值。
def qt_enum(owner: Any, name: str, group: str) -> Any:
    value = getattr(owner, name, None)
    return value if value is not None else getattr(getattr(owner, group), name)


SCROLLBAR_OFF = qt_enum(Qt, "ScrollBarAlwaysOff", "ScrollBarPolicy")
NO_FRAME = qt_enum(QFrame, "NoFrame", "Shape")
USER_ROLE = qt_enum(Qt, "UserRole", "ItemDataRole")
YES = qt_enum(QMessageBox, "Yes", "StandardButton")
NO = qt_enum(QMessageBox, "No", "StandardButton")


ROOT = Path(__file__).resolve().parent
PROGRESS_FILE = ROOT / "progress.json"


# 定义页面模块支持的内容类型。
class ModuleType(Enum):
    TEXT = "text"
    CODE = "code"
    PRACTICE = "practice"


# 保存一道练习题的题目、答案和选项。
@dataclass
class Practice:
    question: str
    answer: str
    choices: list[str] = field(default_factory=list)


# 描述页面中的一个通用内容模块。
@dataclass
class Module:
    title: str
    type: ModuleType
    content: str = ""
    practices: list[Practice] = field(default_factory=list)


# 描述一个知识小节页面及其模块。
@dataclass
class Page:
    key: str
    title: str
    modules: list[Module]
    completable: bool = True


# 描述一个章节及其包含的知识页面。
@dataclass
class Chapter:
    key: str
    title: str
    pages: list[Page]


# 创建文本类型的通用模块。
def text(title: str, content: str) -> Module:
    return Module(title, ModuleType.TEXT, dedent(content).strip())


# 创建代码类型的通用模块。
def code(title: str, content: str) -> Module:
    return Module(title, ModuleType.CODE, dedent(content).strip())


# 创建包含若干练习题的通用模块。
def practice(title: str, *items: Practice) -> Module:
    return Module(title, ModuleType.PRACTICE, practices=list(items))


# 创建一道练习题数据。
def item(question: str, answer: str, *choices: str) -> Practice:
    return Practice(question, answer, list(choices))


# 创建一个由任意模块组合而成的知识页面。
def page(
    key: str,
    title: str,
    *modules: Module,
    completable: bool = True,
) -> Page:
    return Page(key, title, list(modules), completable)


# 构建应用中使用的全部课程章节和页面数据。
def build_curriculum() -> list[Chapter]:
    return [
        Chapter(
            "class_intro",
            "一、类是什么",
            [
                page(
                    "what_is_class",
                    "什么是类",
                    text(
                        "知识点讲解",
                        """
                        类是面向对象编程的核心概念，是一种用户自定义的数据类型。
                        
                        它把数据（成员变量）和操作数据的函数（成员函数）封装在一起，形成一个独立的模块。
                        
                        类提供了创建对象的模板，对象是类的实例，拥有类定义的属性和行为。
                        """,
                    ),
                    code(
                        "案例",
                        """
                        class Person { // 定义一个“人”类
                        public:
                            std::string name; // 定义“人”的姓名
                            int age; // 定义“人”的年龄

                            void introduce() const { // 定义“人”的“自我介绍”行为
                                std::cout << name << "，" << age << "岁" << std::endl;
                            }
                        };

                        int main() {
                            Person alice; // 创建一个“人”的对象，命名为alice
                            alice.name = "Alice"; // 设置“人”的姓名
                            alice.age = 20; // 设置“人”的年龄
                            alice.introduce(); // 调用“人”的“自我介绍”行为
                        }
                        """,
                    ),
                    practice(
                        "练习题",
                        item(
                            "类和对象的关系是什么？",
                            "B。类是模板，对象是根据模板创建的实例。",
                            "A. 类是运行中的对象",
                            "B. 类是模板，对象是实例",
                            "C. 两者没有区别",
                        ),
                        item(
                            "把数据和相关行为放在同一个类中体现了什么思想？",
                            "封装。",
                        ),
                    ),
                )
            ],
        ),
        Chapter(
            "class_template",
            "二、类的通用模板",
            [
                page(
                    "template_overview",
                    "总览模板",
                    code(
                        "通用模板",
                        """
                        class MyClass {
                        private:
                            // 私有成员变量
                            Type pri_var1;
                            // 成员函数（同public部分）
                        public:
                            // 公有成员变量
                            Type pub_var1;
                            // 构造函数
                            MyClass(Type arg1, Type arg2): pri_var1(arg1), pub_var1(arg2) {
                                ...
                            }
                            MyClass(const MyClass& another) {
                                ...
                            }
                            MyClass(Type item) {
                                ...
                            }
                            // 析构函数
                            ~MyClass() {

                            }
                            // 成员函数
                            Type func1(args){
                                ...
                            }
                            // 友元函数
                            friend Type freind_func(args) {
                                ...
                            }
                        };
                        """,
                    ),
                    completable=False,
                ),
                page(
                    "member_variables",
                    "1. 成员变量",
                    text(
                        "知识点讲解",
                        """
                        成员变量定义在类内部，用来保存对象的属性。每个对象通常拥有自己的一份
                        非静态成员变量。为了保护数据，成员变量一般放在 private 区域，
                        再通过 public 成员函数提供访问方式。
                        """,
                    ),
                    code(
                        "案例",
                        """
                        class Book {
                        private:
                            string title; //定义了一个string类型的成员变量，表示书籍的标题，可以通过“对象.title”或“对象指针->title”访问。
                            int pages; //定义了一个int类型的成员变量，表示书籍的页数
                        };
                        """,
                    ),
                    practice(
                        "练习题",
                        item(
                            "若定义对象Book novel，以下哪个可以正确访问成员变量title？",
                            "B. novel.title",
                            "A. novel->title",
                            "B. novel.title",
                            "C. Book.title",
                        ),
                    ),
                ),
                page(
                    "member_functions",
                    "2. 成员函数",
                    text(
                        "知识点讲解",
                        """
                        成员函数描述对象的行为，也负责读取或修改对象内部的数据。
                        成员函数可以直接访问同一个类的 private 成员。
                        """,
                    ),
                    code(
                        "案例",
                        """
                        class Light {
                        private:
                            bool is_on = false; // 定义一个布尔类型的成员变量，表示灯的状态，默认为关闭。

                        public:
                            void turnOn() { // 定义一个成员函数，表示打开灯的行为。可以通过“对象.turnOn()”或“对象指针->turnOn()”调用。
                                is_on = true;
                            }
                        };
                        """,
                    ),
                    practice(
                        "练习题",
                        item(
                            """
                            下列代码的输出是什么？
                            Light l1, l2;
                            l1.turnOn();
                            cout << l1.is_on << " " << l2.is_on << endl;
                            """,
                            "true false",
                            ),
                    ),
                ),
                page(
                    "constructors",
                    "3. 构造函数",
                    text(
                        "知识点讲解",
                        """
                        构造函数在对象创建时自动调用，主要用于初始化成员变量。
                        它与类同名且没有返回类型，可以根据参数不同进行重载。
                        常见的构造函数包括：默认构造函数（无参数）、带参构造函数、拷贝构造函数。
                        """,
                    ),
                    code(
                        "案例",
                        """
                        class Point {
                        private:
                            int x;
                            int y;

                        public:
                            Point(int x, int y) : x(x), y(y) {}
                        };
                        """,
                    ),
                    practice(
                        "练习题",
                        item("构造函数什么时候自动调用？", "对象创建时。"),
                        item("void Point(int x, int y) : x(x), y(y) {}这种写法是否正确？", "不正确，构造函数没有返回类型。"),
                    ),
                ),
                page(
                    "destructor",
                    "4. 析构函数",
                    text(
                        "知识点讲解",
                        """
                        析构函数在对象销毁时自动调用，通常负责释放对象持有的资源。
                        常见于成员变量需要手动分配内存或打开文件等场景，例如成员变量包含new得到的指针。
                        它的函数名是在类名前加 ~，没有返回类型，也没有参数，只能有一个。
                        """,
                    ),
                    code(
                        "案例",
                        """
                        class Message {
                        public:
                            ~Message() {
                                std::cout << "对象被销毁" << std::endl;
                            }
                        };
                        """,
                    ),
                    practice(
                        "练习题",
                        item("如果一个类不定义析构函数，会编译错误吗？", "编译器会生成一个默认析构函数。"),
                    ),
                ),
                page(
                    "friend_function",
                    "5. 友元",
                    text(
                        "知识点讲解",
                        """
                        被声明为 friend 的普通函数或其他类，可以访问当前类的 private 和 protected 成员。
                        
                        友元适合类之间需要紧密协作的场景，但会削弱封装，因此应该控制使用范围。
                        """,
                    ),
                    code(
                        "案例",
                        """
                        class Score {
                        private:
                            int value = 100;

                        public:
                            friend void showScore(const Score& score);
                        };

                        void showScore(const Score& score) {
                            std::cout << score.value << std::endl;
                        }
                        """,
                    ),
                    practice(
                        "练习题",
                        item("声明友元使用哪个关键字？", "friend。"),
                    ),
                ),
                page(
                    "public_private",
                    "6. 公有和私有",
                    text(
                        "知识点讲解",
                        """
                        public 成员可以从类外部直接访问；private 成员只能由类自身及其友元访问；
                        protected 成员还允许派生类访问。
                        
                        为了更好地封装数据，常见设计是把数据设为 private，把操作接口设为 public。
                        """,
                    ),
                    code(
                        "案例",
                        """
                        class Account {
                        private:
                            double balance = 0;

                        public:
                            int account_number;

                            void deposit(double amount) {
                                if (amount > 0) {
                                    balance += amount;
                                }
                            }

                            double getBalance() const {
                                return balance;
                            }
                        };
                        """,
                    ),
                    practice(
                        "练习题",
                        item("类中未写访问限定符时，成员默认是什么权限？", "private。"),
                    ),
                ),
            ],
        ),
        Chapter(
            "person_case",
            "三、Person 类案例",
            [
                page(
                    "person_case_analysis",
                    "Person 类综合分析",
                    text(
                        "设计思路",
                        """
                        Person 类把身份证号设为 private，避免外部随意修改；姓名和年龄作为对象属性；
                        构造函数负责初始化；getter 和 setter 提供受控访问；普通成员函数描述行为；
                        友元函数用于需要读取私有身份证号的身份核验。
                        """,
                    ),
                    code(
                        "Person 类定义",
                        """
                        class Person {
                        private:
                            string id_card; // 身份证号属于敏感数据，类外部不能直接访问。

                        public:
                            string name; // public成员可以在类外部直接访问。
                            int age;

                            Person() {} // 默认构造函数。

                            // 带参构造函数，使用初始化列表设置三个成员变量。
                            Person(string id_card, string name, int age)
                                : id_card(id_card), name(name), age(age) {}

                            // 拷贝构造函数，根据已有Person对象创建新对象。
                            Person(const Person& another)
                                : id_card(another.id_card), name(another.name), age(another.age) {}

                            // 将一行字符串解析为身份证号、姓名和年龄。
                            Person(string input) {
                                stringstream ss(input);
                                ss >> id_card >> name >> age;
                            }

                            ~Person() {} // 对象销毁时自动调用析构函数。

                            // public成员函数为private数据提供安全的修改接口。
                            void set_id_card(string id) {
                                id_card = id;
                            }

                            // 类外部通过该函数读取private成员id_card。
                            string get_id_card() const {
                                return id_card;
                            }

                            void show_id_card() const {
                                cout << "ID Card: " << id_card << endl;
                            }

                            // 普通成员函数，用来描述Person对象的行为。
                            void exercise() const {
                                cout << name << " is exercising." << endl;
                            }

                            // 友元函数不是成员函数，但可以访问private成员id_card。
                            friend void GaokaoChecking(const Person& person, const string& write_id_card) {
                                if (person.id_card == write_id_card) {
                                    cout << "ID card matches. " << person.name << " can take the Gaokao." << endl;
                                } else {
                                    cout << "ID card does not match. " << person.name << " cannot take the Gaokao." << endl;
                                }
                            }
                        };
                        """,
                    ),
                    code(
                        "Person 类的使用",
                        """
                        int main() {
                            // 使用带参构造函数，同时初始化身份证号、姓名和年龄。
                            Person Alice("0987654321", "Alice", 20);

                            // age是public成员，因此可以直接访问。
                            cout << "Alice's age is " << Alice.age << endl;

                            // id_card是private成员，需要通过public成员函数读取。
                            cout << "Alice's ID card is " << Alice.get_id_card() << endl;

                            // 调用成员函数，表示Alice对象执行锻炼行为。
                            Alice.exercise();

                            // 使用字符串解析构造函数创建Bob对象。
                            Person Bob("None Bob 0");

                            // public成员可以直接修改，private成员通过set函数修改。
                            Bob.age = 18;
                            Bob.set_id_card("1234567890");

                            // 友元函数可以读取Bob的private身份证号并完成核验。
                            GaokaoChecking(Bob, "1234567890");

                            return 0;
                        }
                        """,
                    ),
                    practice(
                        "练习题",
                        item("为什么 id_card 适合设为 private？", "防止类外部随意读取或修改敏感数据。"),
                        item("GaokaoChecking 为什么能够访问 id_card？", "它在 Person 类中被声明为友元函数。"),
                    ),
                )
            ],
        ),
        Chapter(
            "inheritance_poly",
            "四、继承、派生与多态",
            [
                page(
                    "inheritance_overview",
                    "总览模板",
                    code(
                        "通用模板",
                        """
                        class Base { // 基类（父类）
                        private:
                            int data; // 基类的成员变量

                        public:
                            int pub_data; // 基类的公有成员变量

                            virtual void introduce() const {
                                std::cout << "Base" << std::endl;
                            }

                            virtual ~Base() = default;
                        };

                        class Derived : public Base { // 派生类（子类）通过 public 继承自 Base
                        private:
                            int extra_data; // 派生类可以添加新的成员变量

                        public:
                            void introduce() const override {
                                std::cout << "Derived" << std::endl;
                            }
                        };
                        """,
                    ),
                    completable=False,
                ),
                page(
                    "inheritance_core",
                    "1. 继承与派生",
                    text(
                        "知识点讲解",
                        """
                        继承让派生类复用基类已有的状态和行为。“派生”等价于“被继承”
                        
                        public/protected/private 继承的核心是压缩访问权限，比如：

                        public继承中，基类的public成员在派生类中仍是public，protected成员在派生类中仍是protected，private成员在派生类中不可访问；

                        protected继承中，基类的public和protected成员在派生类中都变为protected，private成员在派生类中不可访问；

                        private继承中，基类的public和protected成员在派生类中都变为private，private成员在派生类中不可访问。

                        派生类构造函数应先调用基类构造函数，再初始化自己的成员。
                        """,
                    ),
                    code(
                        "案例",
                        """
                        class Person {
                        protected:
                            std::string name;  // 基类的成员变量

                        public:
                            Person(const std::string& name) : name(name) {} // 基类构造函数
                        };

                        class Student : private Person { // private继承，让继承的protected变量name在Student中变为private，外部无法访问。
                        private:
                            std::string major; // 派生类添加新的成员变量

                        public:
                            Student(
                                const std::string& name,
                                const std::string& major
                            ) : Person(name), major(major) {}
                        };
                        """,
                    ),
                    practice(
                        "练习题",
                        item("如果子类public继承了基类，外部能否访问基类的private成员？", "不能访问。继承只会压缩访问权限。"),
                    ),
                ),
                page(
                    "polymorphism_core",
                    "2. 多态",
                    text(
                        "知识点讲解",
                        """
                        运行时多态依靠继承、虚函数以及基类指针或引用实现。

                        基类函数声明为 virtual 后，派生类可以使用 override 重写。

                        调用哪个版本由对象的真实类型决定。
                        """,
                    ),
                    code(
                        "案例",
                        """
                        class Animal {
                        public:
                            virtual void speak() const {
                                std::cout << "动物发出声音" << std::endl;
                            }

                            virtual ~Animal() = default;
                        };

                        class Dog : public Animal {
                        public:
                            void speak() const override {
                                std::cout << "汪汪" << std::endl;
                            }
                        };

                        int main() {
                            Dog dog;
                            Animal* animal = &dog;
                            animal->speak();
                        }
                        """,
                    ),
                    practice(
                        "练习题",
                        item("运行时多态的核心关键字是什么？", "virtual。"),
                        item("override 的作用是什么？", "明确表示派生类正在重写基类虚函数。"),
                    ),
                ),
            ],
        ),
        Chapter(
            "family_case",
            "五、Student 类案例",
            [
                page(
                    "family_case_analysis",
                    "Student 类综合分析",
                    text(
                        "继承关系",
                        """
                        Person 是共同基类。Teacher 和 Student 直接继承 Person；
                        Undergraduate 和 Graduate 再继承 Student。

                        Student 提供虚函数 graduate，不同学生类型重写它，从而通过 Student
                        指针调用不同版本，体现运行时多态。
                        """,
                    ),
                    code(
                        "Student 类的继承/派生",
                        """
                        class Person {
                        private:
                            string id_card;
                        public:
                            string name;
                            int age;
                        };

                        class Teacher : public Person { // “Teacher”都是人，因此继承自“Person”类。且拥有“id_card”（私有）和“name”、“age”（公有）。
                        public:
                            string subject; // “Teacher”有教学的科目，因此相比“Person”多了一个属性。
                        };

                        class Student : public Person { // “Student”都是人，因此继承自“Person”类。同样拥有“Person”的三个属性。
                        private:
                            string student_id;
                        public:
                            string school;

                            virtual void graduate() { // “Student”有毕业的行为，因此定义graduate()函数。
                                cout << "Student graduates from school." << endl;
                            }
                        };

                        class Undergraduate : public Student {
                        public:
                            float gpa;

                            virtual void graduate() override { // 希望在graduate()里同时输出GPA信息，因此使用虚函数重写。
                                cout << "Undergraduate student graduates with GPA: " << gpa << endl;
                            }
                        };

                        class Graduate : public Student {
                        public:
                            string research_area;

                            virtual void graduate() override { // 希望在graduate()里同时输出研究领域信息，因此使用虚函数重写。
                                cout << "Graduate student graduates with research area: " << research_area << endl;
                            }
                        };

                        int main() {
                            Student Alice;
                            Undergraduate Bob;
                            Bob.gpa = 3.8;
                            Student* p_A = &Alice;
                            Student* p_B = &Bob;

                            p_A->graduate(); // 调用 Student::graduate()
                            p_B->graduate(); // 调用 Undergraduate::graduate()，体现多态。
                        }
                        """,
                    ),
                    practice(
                        "练习题",
                        item("Teacher 和 Student 与 Person 是什么关系？", "它们都是 Person 的派生类。"),
                        item(
                            "Student* 指向 Undergraduate 后调用 graduate，会执行哪个版本？",
                            "Undergraduate::graduate()，因为 graduate 是虚函数。",
                        ),
                    ),
                )
            ],
        ),
    ]


# 负责读取、保存和更新本地学习状态。
class ProgressStore:
    # 初始化进度文件路径并读取已有状态。
    def __init__(self, path: Path):
        self.path = path
        self.completed: dict[str, list[str]] = {}
        self.last_page: dict[str, str] = {}
        self.load()

    # 从进度文件中加载已完成小节和上次页面。
    def load(self) -> None:
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        completed = data.get("completed_sections", {})
        last_page = data.get("last_section", {})
        if isinstance(completed, dict):
            self.completed = {
                key: [value for value in values if isinstance(value, str)]
                for key, values in completed.items()
                if isinstance(key, str) and isinstance(values, list)
            }
        if isinstance(last_page, dict):
            self.last_page = {
                key: value
                for key, value in last_page.items()
                if isinstance(key, str) and isinstance(value, str)
            }

    # 将当前学习状态写入进度文件。
    def save(self) -> None:
        data = {
            "completed_sections": self.completed,
            "last_section": self.last_page,
        }
        self.path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # 记录指定章节中最后访问的页面。
    def remember(self, chapter_key: str, page_key: str) -> None:
        self.last_page[chapter_key] = page_key
        self.save()

    # 判断指定知识小节是否已经完成。
    def is_completed(self, chapter_key: str, page_key: str) -> bool:
        return page_key in self.completed.get(chapter_key, [])

    # 在已完成和未完成之间切换小节状态。
    def toggle(self, chapter_key: str, page_key: str) -> None:
        pages = self.completed.setdefault(chapter_key, [])
        if page_key in pages:
            pages.remove(page_key)
        else:
            pages.append(page_key)
        self.remember(chapter_key, page_key)

    # 清空全部完成状态和页面访问记录。
    def reset(self) -> None:
        self.completed.clear()
        self.last_page.clear()
        self.save()

    # 根据小节完成情况计算章节的文字状态。
    def chapter_status(self, chapter: Chapter) -> str:
        pages = [current for current in chapter.pages if current.completable]
        completed = sum(
            self.is_completed(chapter.key, current.key)
            for current in pages
        )
        if completed == len(pages):
            return "已完成"
        if completed:
            return "学习中"
        return "未完成"


# 为模块内容生成统一字体和排版的 HTML 文档。
def html_document(content: str, monospace: bool = False) -> str:
    family = "'Cascadia Mono', Consolas" if monospace else "'Microsoft YaHei UI'"
    return f"""
    <style>
        body {{
            color: #23323c;
            font-family: {family};
            font-size: 14px;
            line-height: 1.7;
            margin: 0;
        }}
        pre {{
            font-family: 'Cascadia Mono', Consolas;
            font-size: 14px;
            line-height: 1.5;
            white-space: pre-wrap;
        }}
    </style>
    {content}
    """


# 将纯文本内容转换为分段显示的 HTML。
def text_html(content: str) -> str:
    paragraphs = "".join(
        f"<p>{escape(paragraph)}</p>"
        for paragraph in content.split("\n\n")
        if paragraph.strip()
    )
    return html_document(paragraphs)


# 将代码转换为 HTML，并把双斜线注释标记为绿色。
def code_html(content: str) -> str:
    escaped = escape(content)
    lines = []
    for line in escaped.splitlines():
        comment_at = line.find("//")
        if comment_at >= 0:
            line = (
                line[:comment_at]
                + '<span style="color:#2f8f46">'
                + line[comment_at:]
                + "</span>"
            )
        lines.append(line)
    return html_document(f"<pre>{'\n'.join(lines)}</pre>", monospace=True)


# 根据文档内容自动调整高度的只读文本浏览器。
class AutoHeightBrowser(QTextBrowser):
    # 初始化浏览器并关闭内部滚动条。
    def __init__(self):
        super().__init__()
        self.document().setDocumentMargin(0)
        self.setOpenLinks(False)
        self.setOpenExternalLinks(False)
        self.setVerticalScrollBarPolicy(SCROLLBAR_OFF)
        self.setHorizontalScrollBarPolicy(SCROLLBAR_OFF)

    # 设置 HTML 内容并立即重新计算控件高度。
    def set_content(self, content: str) -> None:
        self.setHtml(content)
        self.update_height()

    # 根据当前文档尺寸调整浏览器固定高度。
    def update_height(self) -> None:
        document = self.document()
        document.setTextWidth(max(1, self.viewport().width()))
        height = document.documentLayout().documentSize().height()
        self.setFixedHeight(max(90, int(height) + 20))

    # 在控件宽度变化后重新计算内容高度。
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.update_height()


# 使用统一卡片样式渲染文本、代码或练习模块。
class ModuleCard(QFrame):
    # 根据模块类型创建对应的卡片内容。
    def __init__(self, module: Module):
        super().__init__()
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        title = QLabel(module.title)
        title.setObjectName("cardTitle")
        layout.addWidget(title)

        if module.type == ModuleType.PRACTICE:
            self.add_practices(layout, module.practices)
            return

        browser = AutoHeightBrowser()
        browser.setObjectName("content")
        browser.set_content(
            code_html(module.content)
            if module.type == ModuleType.CODE
            else text_html(module.content)
        )
        layout.addWidget(browser)

    # 向模块卡片中添加可显示和隐藏答案的练习题。
    def add_practices(
        self,
        layout: QVBoxLayout,
        practices: list[Practice],
    ) -> None:
        for number, current in enumerate(practices, start=1):
            frame = QFrame()
            frame.setObjectName("practice")
            practice_layout = QVBoxLayout(frame)

            question = QLabel(f"{number}. {current.question}")
            question.setWordWrap(True)
            question.setObjectName("question")
            practice_layout.addWidget(question)

            for choice in current.choices:
                label = QLabel(choice)
                label.setWordWrap(True)
                practice_layout.addWidget(label)

            answer = QLabel(f"答案：{current.answer}")
            answer.setWordWrap(True)
            answer.setObjectName("answer")
            answer.hide()
            practice_layout.addWidget(answer)

            button = QPushButton("显示答案")
            button.setCheckable(True)
            button.setObjectName("answerButton")
            button.toggled.connect(answer.setVisible)
            button.toggled.connect(
                lambda checked, target=button: target.setText(
                    "隐藏答案" if checked else "显示答案"
                )
            )
            practice_layout.addWidget(button)
            layout.addWidget(frame)


# 显示单个章节中的知识页面和底部导航。
class KnowledgePage(QWidget):
    # 初始化章节页面并保存导航及刷新回调。
    def __init__(
        self,
        chapter: Chapter,
        progress: ProgressStore,
        navigate: Callable[[str, str], None],
        refresh: Callable[[], None],
    ):
        super().__init__()
        self.chapter = chapter
        self.progress = progress
        self.navigate = navigate
        self.refresh_views = refresh
        self.current = chapter.pages[0]

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        header = QFrame()
        header.setObjectName("hero")
        header_layout = QVBoxLayout(header)
        title = QLabel(chapter.title)
        title.setObjectName("heroTitle")
        header_layout.addWidget(title)
        root.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(NO_FRAME)
        root.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)
        self.layout = QVBoxLayout(container)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(12)

    # 加载指定知识小节并重新生成页面模块。
    def load(self, page_key: str) -> None:
        self.current = next(
            (current for current in self.chapter.pages if current.key == page_key),
            self.chapter.pages[0],
        )
        self.clear()

        title = QLabel(self.current.title)
        title.setObjectName("pageTitle")
        self.layout.addWidget(title)

        for module in self.current.modules:
            self.layout.addWidget(ModuleCard(module))

        self.layout.addWidget(self.build_footer())
        self.layout.addStretch()
        self.progress.remember(self.chapter.key, self.current.key)

    # 清除当前页面布局中的全部控件。
    def clear(self) -> None:
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    # 创建上一节、完成切换和下一节组成的底部导航。
    def build_footer(self) -> QFrame:
        footer = QFrame()
        footer.setObjectName("card")
        layout = QHBoxLayout(footer)

        index = self.chapter.pages.index(self.current)
        previous = QPushButton("上一节")
        previous.setEnabled(index > 0)
        previous.clicked.connect(lambda: self.move(-1))
        layout.addWidget(previous)

        if self.current.completable:
            self.complete_button = QPushButton()
            self.complete_button.setCheckable(True)
            self.complete_button.setObjectName("completeButton")
            self.complete_button.clicked.connect(self.toggle_complete)
            layout.addWidget(self.complete_button, 1)
            self.update_complete_button()
        else:
            layout.addStretch()

        next_button = QPushButton("下一节")
        next_button.setEnabled(index < len(self.chapter.pages) - 1)
        next_button.clicked.connect(lambda: self.move(1))
        layout.addWidget(next_button)
        return footer

    # 按相对位置切换到上一节或下一节。
    def move(self, offset: int) -> None:
        index = self.chapter.pages.index(self.current) + offset
        if 0 <= index < len(self.chapter.pages):
            self.navigate(self.chapter.key, self.chapter.pages[index].key)

    # 切换当前知识小节的完成状态。
    def toggle_complete(self) -> None:
        self.progress.toggle(self.chapter.key, self.current.key)
        self.update_complete_button()
        self.refresh_views()

    # 根据完成状态更新完成按钮的文字和选中状态。
    def update_complete_button(self) -> None:
        if not self.current.completable:
            return
        completed = self.progress.is_completed(
            self.chapter.key,
            self.current.key,
        )
        self.complete_button.setChecked(completed)
        self.complete_button.setText("取消已学会" if completed else "我学会了")

    # 从进度存储中刷新当前页面状态。
    def refresh(self) -> None:
        if self.current.completable and hasattr(self, "complete_button"):
            self.update_complete_button()


# 展示全部章节和知识小节完成状态的学习总览。
class ChapterList(QWidget):
    # 初始化总览页面并创建章节与小节状态控件。
    def __init__(
        self,
        chapters: list[Chapter],
        progress: ProgressStore,
        navigate: Callable[[str, str], None],
    ):
        super().__init__()
        self.chapters = chapters
        self.progress = progress
        self.chapter_status: dict[str, QLabel] = {}
        self.page_status: dict[tuple[str, str], QLabel] = {}
        self.page_buttons: dict[tuple[str, str], QPushButton] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(NO_FRAME)
        root.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        hero = QFrame()
        hero.setObjectName("hero")
        hero_layout = QVBoxLayout(hero)
        title = QLabel("学习总览")
        title.setObjectName("heroTitle")
        hero_layout.addWidget(title)
        hero_layout.addWidget(QLabel("按知识小节记录完成状态"))
        layout.addWidget(hero)

        for chapter in chapters:
            card = QFrame()
            card.setObjectName("card")
            card_layout = QVBoxLayout(card)

            header = QHBoxLayout()
            chapter_button = QPushButton(chapter.title)
            chapter_button.setObjectName("overviewButton")
            chapter_button.clicked.connect(
                lambda _, current=chapter: navigate(
                    current.key,
                    current.pages[0].key,
                )
            )
            header.addWidget(chapter_button, 1)

            status = QLabel()
            status.setObjectName("status")
            header.addWidget(status)
            self.chapter_status[chapter.key] = status
            card_layout.addLayout(header)

            for current in chapter.pages:
                if not current.completable:
                    continue
                row = QFrame()
                row.setObjectName("practice")
                row_layout = QHBoxLayout(row)
                button = QPushButton(current.title)
                button.setObjectName("overviewButton")
                button.clicked.connect(
                    lambda _, chapter_key=chapter.key, page_key=current.key:
                    navigate(chapter_key, page_key)
                )
                row_layout.addWidget(button, 1)
                page_status = QLabel()
                page_status.setObjectName("status")
                row_layout.addWidget(page_status)
                card_layout.addWidget(row)
                key = (chapter.key, current.key)
                self.page_buttons[key] = button
                self.page_status[key] = page_status

            layout.addWidget(card)
        layout.addStretch()

    # 设置状态标签的文字及对应颜色。
    def set_status(self, label: QLabel, status: str) -> None:
        colors = {
            "已完成": ("#e6f6ea", "#2f7a43"),
            "学习中": ("#fff4d9", "#8a6200"),
            "未完成": ("#edf1f4", "#687782"),
        }
        background, color = colors[status]
        label.setText(status)
        label.setStyleSheet(
            f"background:{background};color:{color};"
            "border-radius:10px;padding:4px 10px;font-weight:700;"
        )

    # 根据最新进度刷新全部章节和小节状态。
    def refresh(self) -> None:
        for chapter in self.chapters:
            self.set_status(
                self.chapter_status[chapter.key],
                self.progress.chapter_status(chapter),
            )
            for current in chapter.pages:
                if not current.completable:
                    continue
                completed = self.progress.is_completed(
                    chapter.key,
                    current.key,
                )
                key = (chapter.key, current.key)
                self.set_status(
                    self.page_status[key],
                    "已完成" if completed else "未完成",
                )
                prefix = "✅ " if completed else "⭕ "
                self.page_buttons[key].setText(prefix + current.title)


# 组织侧边导航、学习总览和知识页面的主窗口。
class MainWindow(QMainWindow):
    # 初始化课程数据、进度存储和全部界面组件。
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MetaLearning")
        self.resize(1024, 720)
        self.setMinimumSize(900, 640)

        self.chapters = build_curriculum()
        self.progress = ProgressStore(PROGRESS_FILE)
        self.syncing = False
        self.chapter_items: dict[str, QTreeWidgetItem] = {}
        self.page_items: dict[tuple[str, str], QTreeWidgetItem] = {}

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(18)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setMinimumWidth(280)
        sidebar_layout = QVBoxLayout(sidebar)
        root.addWidget(sidebar)

        self.navigation = QTreeWidget()
        self.navigation.setObjectName("navigation")
        self.navigation.setHeaderHidden(True)
        self.navigation.setIndentation(0)
        self.navigation.currentItemChanged.connect(self.navigation_changed)
        sidebar_layout.addWidget(self.navigation)

        reset = QPushButton("重置学习状态")
        reset.clicked.connect(self.reset)
        sidebar_layout.addWidget(reset)

        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)

        self.chapterList = ChapterList(
            self.chapters,
            self.progress,
            self.show_page,
        )
        self.stack.addWidget(self.chapterList)

        self.knowledge_pages: dict[str, KnowledgePage] = {}
        for chapter in self.chapters:
            knowledge_page = KnowledgePage(
                chapter,
                self.progress,
                self.show_page,
                self.refresh_views,
            )
            self.knowledge_pages[chapter.key] = knowledge_page
            self.stack.addWidget(knowledge_page)

        self.build_navigation()
        self.refresh_views()
        self.show_chapterList()

    # 根据课程数据创建侧边栏导航项目。
    def build_navigation(self) -> None:
        self.chapterList_item = QTreeWidgetItem(["学习总览"])
        self.chapterList_item.setData(0, USER_ROLE, "chapterList")
        self.navigation.addTopLevelItem(self.chapterList_item)

        for chapter in self.chapters:
            chapter_item = QTreeWidgetItem([chapter.title])
            chapter_item.setData(
                0,
                USER_ROLE,
                (chapter.key, chapter.pages[0].key),
            )
            self.navigation.addTopLevelItem(chapter_item)
            self.chapter_items[chapter.key] = chapter_item

            if any(not current.completable for current in chapter.pages):
                for current in chapter.pages:
                    if not current.completable:
                        continue
                    page_item = QTreeWidgetItem([current.title])
                    page_item.setData(
                        0,
                        USER_ROLE,
                        (chapter.key, current.key),
                    )
                    self.navigation.addTopLevelItem(page_item)
                    self.page_items[(chapter.key, current.key)] = page_item

    # 响应侧边栏选中项变化并切换页面。
    def navigation_changed(
        self,
        current: QTreeWidgetItem | None,
        previous: QTreeWidgetItem | None,
    ) -> None:
        del previous
        if self.syncing or current is None:
            return
        target = current.data(0, USER_ROLE)
        if target == "chapterList":
            self.show_chapterList()
        elif isinstance(target, tuple):
            self.show_page(*target)

    # 在不重复触发导航回调的情况下选中项目。
    def select_item(self, item: QTreeWidgetItem) -> None:
        self.syncing = True
        self.navigation.setCurrentItem(item)
        self.syncing = False

    # 切换到学习总览页面。
    def show_chapterList(self) -> None:
        self.select_item(self.chapterList_item)
        self.stack.setCurrentWidget(self.chapterList)
        self.chapterList.refresh()

    # 切换到指定章节中的指定知识页面。
    def show_page(self, chapter_key: str, page_key: str) -> None:
        item = self.page_items.get(
            (chapter_key, page_key),
            self.chapter_items[chapter_key],
        )
        self.select_item(item)
        knowledge_page = self.knowledge_pages[chapter_key]
        knowledge_page.load(page_key)
        self.stack.setCurrentWidget(knowledge_page)
        self.refresh_views()

    # 刷新总览、侧边栏和知识页面的完成状态。
    def refresh_views(self) -> None:
        self.chapterList.refresh()
        for chapter in self.chapters:
            completed = self.progress.chapter_status(chapter) == "已完成"
            prefix = "✅ " if completed else "⭕ "
            self.chapter_items[chapter.key].setText(0, prefix + chapter.title)
            for current in chapter.pages:
                item_widget = self.page_items.get((chapter.key, current.key))
                if item_widget:
                    completed = self.progress.is_completed(
                        chapter.key,
                        current.key,
                    )
                    prefix = "✅ " if completed else "⭕ "
                    item_widget.setText(0, prefix + current.title)
        for knowledge_page in self.knowledge_pages.values():
            knowledge_page.refresh()

    # 经用户确认后重置全部学习状态。
    def reset(self) -> None:
        result = QMessageBox.question(
            self,
            "确认重置",
            "这会清空所有小节的完成状态，是否继续？",
            YES | NO,
            NO,
        )
        if result == YES:
            self.progress.reset()
            self.refresh_views()
            self.show_chapterList()


STYLE_SHEET = """
QWidget {
    background: #f3f5f7;
    color: #23323c;
    font-family: "Microsoft YaHei UI";
    font-size: 14px;
}
QFrame#sidebar, QFrame#hero, QFrame#card {
    background: #ffffff;
    border: 1px solid #dce4eb;
    border-radius: 18px;
}
QLabel#heroTitle {
    color: #1f3b4d;
    font-size: 28px;
    font-weight: 700;
}
QLabel#pageTitle {
    color: #1f3b4d;
    font-size: 22px;
    font-weight: 700;
}
QLabel#cardTitle {
    color: #1f3b4d;
    font-size: 18px;
    font-weight: 700;
}
QTextBrowser#content {
    background: #ffffff;
    border: 1px solid #dce4eb;
    border-radius: 12px;
    padding: 8px;
}
QTreeWidget#navigation {
    background: #ffffff;
    border: 1px solid #dce4eb;
    border-radius: 14px;
    padding: 8px;
    outline: 0;
}
QTreeWidget#navigation::item {
    border-radius: 10px;
    padding: 9px 11px;
    margin: 2px 0;
}
QTreeWidget#navigation::item:selected {
    background: #d8e6f1;
    color: #17384c;
}
QPushButton {
    background: #3f6c89;
    color: white;
    border: none;
    border-radius: 11px;
    padding: 10px 14px;
    font-weight: 600;
}
QPushButton:hover {
    background: #345a72;
}
QPushButton:disabled {
    background: #e6ebef;
    color: #8b97a0;
}
QPushButton#completeButton:checked {
    background: #5d6d78;
}
QPushButton#overviewButton {
    background: #ffffff;
    color: #1f3b4d;
    border: 1px solid #dce4eb;
    text-align: left;
}
QFrame#practice {
    background: #fbfcfd;
    border: 1px solid #e3e9ee;
    border-radius: 12px;
}
QLabel#question {
    color: #1f3b4d;
    font-weight: 700;
}
QLabel#answer {
    background: #eef6fb;
    color: #23465a;
    border: 1px solid #d5e5ef;
    border-radius: 10px;
    padding: 10px;
}
QPushButton#answerButton {
    background: #f8fafc;
    color: #2a566f;
    border: 1px dashed #b8ccd9;
}
"""


# 创建 Qt 应用并启动主窗口事件循环。
def main() -> int:
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_SHEET)
    window = MainWindow()
    window.show()
    return app.exec() if hasattr(app, "exec") else app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
