-- 创建测试数据库结构和数据

-- 创建员工表
CREATE TABLE IF NOT EXISTS employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '员工ID',
    first_name VARCHAR(50) NOT NULL COMMENT '名',
    last_name VARCHAR(50) NOT NULL COMMENT '姓',
    email VARCHAR(100) UNIQUE COMMENT '电子邮件',
    phone_number VARCHAR(20) COMMENT '电话号码',
    hire_date DATE NOT NULL COMMENT '入职日期',
    job_id INT NOT NULL COMMENT '职位ID',
    salary DECIMAL(10, 2) COMMENT '薪资',
    manager_id INT COMMENT '经理ID',
    department_id INT COMMENT '部门ID'
) COMMENT '员工信息表';

-- 创建部门表
CREATE TABLE IF NOT EXISTS departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '部门ID',
    department_name VARCHAR(100) NOT NULL COMMENT '部门名称',
    manager_id INT COMMENT '部门经理ID',
    location_id INT COMMENT '位置ID'
) COMMENT '部门信息表';

-- 创建职位表
CREATE TABLE IF NOT EXISTS jobs (
    job_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '职位ID',
    job_title VARCHAR(100) NOT NULL COMMENT '职位名称',
    min_salary DECIMAL(10, 2) COMMENT '最低薪资',
    max_salary DECIMAL(10, 2) COMMENT '最高薪资'
) COMMENT '职位信息表';

-- 创建位置表
CREATE TABLE IF NOT EXISTS locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '位置ID',
    street_address VARCHAR(100) COMMENT '街道地址',
    postal_code VARCHAR(20) COMMENT '邮政编码',
    city VARCHAR(50) NOT NULL COMMENT '城市',
    state_province VARCHAR(50) COMMENT '省/州',
    country_id CHAR(2) COMMENT '国家ID'
) COMMENT '位置信息表';

-- 创建国家表
CREATE TABLE IF NOT EXISTS countries (
    country_id CHAR(2) PRIMARY KEY COMMENT '国家ID',
    country_name VARCHAR(100) COMMENT '国家名称',
    region_id INT COMMENT '地区ID'
) COMMENT '国家信息表';

-- 添加外键约束
ALTER TABLE employees
    ADD CONSTRAINT fk_emp_dept FOREIGN KEY (department_id) REFERENCES departments(department_id),
    ADD CONSTRAINT fk_emp_job FOREIGN KEY (job_id) REFERENCES jobs(job_id),
    ADD CONSTRAINT fk_emp_manager FOREIGN KEY (manager_id) REFERENCES employees(employee_id);

ALTER TABLE departments
    ADD CONSTRAINT fk_dept_mgr FOREIGN KEY (manager_id) REFERENCES employees(employee_id),
    ADD CONSTRAINT fk_dept_loc FOREIGN KEY (location_id) REFERENCES locations(location_id);

ALTER TABLE locations
    ADD CONSTRAINT fk_loc_country FOREIGN KEY (country_id) REFERENCES countries(country_id);

-- 插入示例数据

-- 国家数据
INSERT INTO countries (country_id, country_name, region_id) VALUES
('CN', '中国', 3),
('US', '美国', 2),
('UK', '英国', 1),
('JP', '日本', 3),
('DE', '德国', 1);

-- 位置数据
INSERT INTO locations (street_address, postal_code, city, state_province, country_id) VALUES
('朝阳区建国路88号', '100022', '北京', '北京', 'CN'),
('浦东新区张江高科技园区', '201203', '上海', '上海', 'CN'),
('123 Main Street', '10001', '纽约', '纽约州', 'US'),
('456 Oxford Street', 'W1D 1AB', '伦敦', '英格兰', 'UK'),
('新宿区西新宿2-8-1', '160-0023', '东京', '东京都', 'JP');

-- 职位数据
INSERT INTO jobs (job_title, min_salary, max_salary) VALUES
('软件工程师', 8000.00, 20000.00),
('产品经理', 12000.00, 25000.00),
('销售代表', 6000.00, 15000.00),
('人力资源专员', 7000.00, 18000.00),
('财务经理', 15000.00, 30000.00),
('技术总监', 25000.00, 50000.00),
('市场专员', 8000.00, 16000.00),
('CEO', 50000.00, 100000.00);

-- 先插入没有经理的员工
INSERT INTO employees (first_name, last_name, email, phone_number, hire_date, job_id, salary, manager_id, department_id) VALUES
('李', '明', 'liming@example.com', '13800138001', '2015-01-15', 8, 80000.00, NULL, NULL);

-- 部门数据
INSERT INTO departments (department_name, manager_id, location_id) VALUES
('研发部', 1, 1),
('产品部', NULL, 1),
('销售部', NULL, 2),
('人力资源部', NULL, 1),
('财务部', NULL, 2);

-- 更新之前插入的员工数据
UPDATE employees SET department_id = 1 WHERE employee_id = 1;

-- 插入剩余员工数据
INSERT INTO employees (first_name, last_name, email, phone_number, hire_date, job_id, salary, manager_id, department_id) VALUES
('王', '芳', 'wangfang@example.com', '13800138002', '2016-03-20', 6, 40000.00, 1, 1),
('张', '伟', 'zhangwei@example.com', '13800138003', '2017-05-10', 1, 15000.00, 2, 1),
('刘', '洋', 'liuyang@example.com', '13800138004', '2018-01-05', 1, 12000.00, 2, 1),
('陈', '静', 'chenjing@example.com', '13800138005', '2016-07-15', 2, 18000.00, 1, 2),
('赵', '鑫', 'zhaoxin@example.com', '13800138006', '2017-10-08', 3, 10000.00, 1, 3),
('杨', '帆', 'yangfan@example.com', '13800138007', '2019-03-12', 3, 9000.00, 6, 3),
('吴', '丽', 'wuli@example.com', '13800138008', '2018-06-22', 4, 12000.00, 1, 4),
('郑', '强', 'zhengqiang@example.com', '13800138009', '2017-08-30', 5, 20000.00, 1, 5);

-- 更新部门经理
UPDATE departments SET manager_id = 2 WHERE department_id = 1;
UPDATE departments SET manager_id = 5 WHERE department_id = 2;
UPDATE departments SET manager_id = 6 WHERE department_id = 3;
UPDATE departments SET manager_id = 8 WHERE department_id = 4;
UPDATE departments SET manager_id = 9 WHERE department_id = 5; 